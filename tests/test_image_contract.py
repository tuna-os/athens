from configparser import ConfigParser
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


def read_mkosi_config(path: Path) -> ConfigParser:
    config = ConfigParser(interpolation=None, strict=False)
    with path.open(encoding="utf-8") as stream:
        config.read_file(stream)
    return config


class AthensImageContractTests(unittest.TestCase):
    def test_mkosi_image_id_stack_and_partition_labels_agree(self) -> None:
        root_config = read_mkosi_config(ROOT / "mkosi.conf")
        image_path = ROOT / "mkosi.images/os/mkosi.conf"
        image_config = read_mkosi_config(image_path)

        self.assertEqual(root_config["Output"]["ImageId"], "athens")
        self.assertEqual(image_config["Output"]["Output"], "athens_%v")
        self.assertEqual(image_config["Content"]["Packages"], "stacks/athens.bst")
        self.assertTrue((ROOT / "elements/stacks/athens.bst").is_file())

        labels = []
        for path in (ROOT / "mkosi.images/os/mkosi.repart").glob("*.conf"):
            labels.extend(re.findall(r"^Label=(.+)$", path.read_text(encoding="utf-8"), re.MULTILINE))
        self.assertTrue(labels)
        self.assertTrue(
            all(label.startswith("athens") or label == "_empty" for label in labels),
            labels,
        )
        image_filter = next(
            line for line in image_config["Content"]["KernelCommandLine"].splitlines()
            if "systemd.image_filter=" in line
        )
        self.assertIn("usr=athens_*", image_filter)
        self.assertIn("root=athens-*", image_filter)

    def test_active_image_has_no_unconfigured_upstream_update_sources(self) -> None:
        update_dir = ROOT / "mkosi.images/os/mkosi.extra/usr/lib/sysupdate.d"
        signing_key = ROOT / "mkosi.images/os/mkosi.extra/usr/lib/systemd/import-pubring.pgp"

        self.assertFalse(list(update_dir.glob("*.transfer")))
        self.assertFalse(signing_key.exists())


if __name__ == "__main__":
    unittest.main()
