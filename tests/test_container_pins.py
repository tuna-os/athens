from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ContainerPinTests(unittest.TestCase):
    def test_local_build_container_is_pinned_by_digest(self) -> None:
        # `just bst` runs this container privileged, with the source tree
        # mounted read-write. A tag is a name the registry can point somewhere
        # else; a digest names the content.
        justfile = (ROOT / "Justfile").read_text(encoding="utf-8")
        default = re.search(
            r'^export bst2_image := env\("BST2_IMAGE", "([^"]+)"\)$', justfile, re.MULTILINE
        )

        self.assertIsNotNone(default)
        self.assertRegex(default.group(1), r"/bst2@sha256:[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
