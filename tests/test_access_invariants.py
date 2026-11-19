from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts/check-image-access.sh"

# Everything the two image builds read from this tree. Junction content is
# not here; scripts/check-image-access.sh reads the built image for that.
IMAGE_INPUTS = (
    "mkosi.conf",
    "mkosi.conf.d/**/*",
    "mkosi.images/**/*",
    "elements/**/*.bst",
    "files/**/*",
)

# Access that is convenient on a test VM and wrong on an installed machine.
# A local test build sets its own (see "Build locally" in README.md).
FORBIDDEN = {
    "root password": re.compile(r"^\s*RootPassword\s*=|(?:hashed|plaintext)-password"),
    "password set or blanked": re.compile(
        r"\bpasswd\s+(?:-d|--delete)\b|\bchpasswd\b|\busermod\b.*\s(?:-p|--password)\b|\bsed\b.*\bshadow\b"
    ),
    "passwordless sudo": re.compile(r"\bNOPASSWD\b"),
    "passwordless login group": re.compile(r"\bnopasswdlogin\b"),
    "autologin": re.compile(
        r"^\s*Autologin\s*=|autologin-user\s*=|AutomaticLogin(?:Enable)?\s*=|--autologin\b"
    ),
}


def violations(text: str) -> list[tuple[int, str]]:
    found = []
    for number, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith("#"):
            continue
        found.extend((number, name) for name, pattern in FORBIDDEN.items() if pattern.search(line))
    return found


class SourceAccessInvariantTests(unittest.TestCase):
    def test_image_inputs_set_no_development_access_defaults(self) -> None:
        inputs = sorted(
            path for pattern in IMAGE_INPUTS for path in ROOT.glob(pattern) if path.is_file()
        )
        self.assertIn(ROOT / "mkosi.images/os/mkosi.conf", inputs)
        self.assertIn(ROOT / "elements/desktop/lightdm.bst", inputs)

        found = [
            f"{path.relative_to(ROOT)}:{number}: {name}"
            for path in inputs
            for number, name in violations(path.read_text(encoding="utf-8", errors="replace"))
        ]

        self.assertEqual(found, [])

    def test_each_default_is_recognised(self) -> None:
        samples = {
            "RootPassword=root": "root password",
            "RootPassword=hashed:": "root password",
            "install -m600 pw %{install-root}/usr/lib/credstore/passwd.hashed-password.root": "root password",
            "passwd -d root": "password set or blanked",
            "echo 'root:root' | chpasswd": "password set or blanked",
            "usermod -p '' athens": "password set or blanked",
            "sed -i 's/^root:[^:]*:/root::/' /etc/shadow": "password set or blanked",
            "echo '%wheel ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/wheel": "passwordless sudo",
            "m athens nopasswdlogin": "passwordless login group",
            "Autologin=yes": "autologin",
            "autologin-user=athens": "autologin",
            "AutomaticLoginEnable=True": "autologin",
            "ExecStart=-agetty --autologin root %I": "autologin",
        }
        for line, name in samples.items():
            with self.subTest(line=line):
                self.assertIn((1, name), violations(line))

        self.assertEqual(violations("# RootPassword=root\n  # NOPASSWD\nchmod 4755 /usr/bin/passwd"), [])


@unittest.skipIf(shutil.which("sh") is None, "no POSIX shell")
class ImageAccessCheckTests(unittest.TestCase):
    def run_check(self, files: dict[str, str]) -> subprocess.CompletedProcess:
        with tempfile.TemporaryDirectory() as root:
            for name, content in files.items():
                path = Path(root, name)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
            return subprocess.run(
                ["sh", str(CHECK), root], capture_output=True, text=True, check=False
            )

    def test_root_without_access_defaults_passes(self) -> None:
        result = self.run_check(
            {
                "etc/shadow": "root:!*:19000::::::\nlightdm:!*:19000::::::\nathens:$y$j9T$salt$hash:19000::::::\n",
                "etc/group": "root:x:0:\nnopasswdlogin:x:990:\nwheel:x:10:athens\n",
                "etc/sudoers": "# %wheel ALL=(ALL) NOPASSWD: ALL\n%wheel ALL=(ALL) ALL\n",
                "etc/lightdm/lightdm.conf": "[Seat:*]\n#autologin-user=\nautologin-user=\n",
                "etc/gdm/custom.conf": "[daemon]\nAutomaticLoginEnable=False\n",
                "usr/lib/credstore/firstboot.locale": "C.UTF-8\n",
            }
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")

    def test_each_access_default_fails(self) -> None:
        cases = {
            "etc/shadow": ("root::19000::::::\n", "'root' has an empty password"),
            "usr/etc/shadow": ("athens::19000::::::", "'athens' has an empty password"),
            "etc/group": ("nopasswdlogin:x:990:athens\n", "nopasswdlogin has members"),
            "etc/sudoers.d/wheel": ("%wheel ALL=(ALL) NOPASSWD: ALL\n", "NOPASSWD rule"),
            "usr/share/factory/etc/sudoers": ("athens ALL=(ALL) NOPASSWD: ALL\n", "NOPASSWD rule"),
            "etc/lightdm/lightdm.conf.d/50-live.conf": (
                "[Seat:*]\nautologin-user=athens\n",
                "display manager autologin",
            ),
            "usr/share/lightdm/lightdm.conf.d/50-live.conf": (
                "[Seat:*]\nautologin-user = athens\n",
                "display manager autologin",
            ),
            "etc/gdm/custom.conf": (
                "[daemon]\nAutomaticLoginEnable=True\n",
                "display manager autologin",
            ),
            "usr/lib/systemd/system/getty@tty1.service.d/autologin.conf": (
                "[Service]\nExecStart=\nExecStart=-agetty --autologin root %I\n",
                "console autologin",
            ),
            "usr/lib/credstore/passwd.hashed-password.root": (
                "$y$j9T$salt$hash\n",
                "root password stored in the image",
            ),
        }
        for name, (content, message) in cases.items():
            with self.subTest(file=name):
                result = self.run_check({name: content})

                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(f"/{name}", result.stderr)
                self.assertIn(message, result.stderr)

    def test_oci_lint_recipe_runs_the_check_on_the_image(self) -> None:
        recipe = (ROOT / "Justfile").read_text(encoding="utf-8").split("\nlint-oci:\n", 1)[1]
        recipe = recipe.split("\n\n", 1)[0]

        self.assertIn("ghcr.io/tuna-os/athens:latest", recipe)
        self.assertIn("< scripts/check-image-access.sh", recipe)


if __name__ == "__main__":
    unittest.main()
