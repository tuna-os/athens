"""Unit admission checks only; these are never Athens image qualification."""
import copy
import hashlib
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("athens_qualification", ROOT / "scripts/qualify-iso.py")
qualification = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qualification)


class SessionAdmission(unittest.TestCase):
    def setUp(self):
        self.expected_bytes = b"independent committed asset"
        self.digest = hashlib.sha256(self.expected_bytes).hexdigest()
        self.state = {
            "boot_id": "installed-boot", "desktop": "Pantheon", "session_type": "wayland",
            "os_release": 'ID="athens"\nNAME="TunaOS Athens"\n',
            "dconf_profile": "user", "schema_directory_override": "", "settings_backend_override": "",
            "artwork_sha256": {"athens-logo.svg": self.digest, "athens-wallpaper.png": self.digest},
            "bootc": {"status": {"booted": {"image": {"imageDigest": "sha256:payload"}}}},
            "background": {},
        }
        for key, value in {"picture-uri": "file:///usr/share/backgrounds/TunaOS/Athens/athens-wallpaper.png",
                           "picture-uri-dark": "file:///usr/share/backgrounds/TunaOS/Athens/athens-wallpaper.png",
                           "picture-options": "zoom"}.items():
            self.state["background"][key] = {"effective": value, "default": value, "user": None, "writable": True}
        self.receipt = {"source": {"source_commit": "source", "payload_manifest_digest": "sha256:payload"},
                        "states": {"live": {"boot_id": "live-boot"}}}
        self.git = patch.object(qualification, "git", return_value=self.expected_bytes)
        self.git.start()
        self.addCleanup(self.git.stop)

    def admit(self, state):
        qualification.validate_state(state, "installed", self.receipt)

    def test_actual_fresh_unlocked_defaults_admitted(self):
        self.admit(self.state)
        self.assertEqual(self.receipt["states"]["installed"], self.state)

    def test_user_value_is_not_proof_of_a_default(self):
        self.state["background"]["picture-uri"]["user"] = self.state["background"]["picture-uri"]["effective"]
        with self.assertRaises(RuntimeError):
            self.admit(self.state)

    def test_locks_wrong_defaults_wrong_desktop_and_test_backends_rejected(self):
        for mutation in (lambda s: s["background"]["picture-uri"].update(writable=False),
                         lambda s: s["background"]["picture-uri"].update(default="upstream"),
                         lambda s: s.update(desktop="GNOME"),
                         lambda s: s.update(settings_backend_override="memory"),
                         lambda s: s.update(schema_directory_override="/tmp/test")):
            state = copy.deepcopy(self.state)
            mutation(state)
            with self.assertRaises(RuntimeError):
                self.admit(state)

    def test_wrong_image_artwork_missing_identity_and_live_boot_rejected(self):
        for mutation in (lambda s: s["bootc"]["status"]["booted"]["image"].update(imageDigest="sha256:old"),
                         lambda s: s["artwork_sha256"].update({"athens-logo.svg": "wrong"}),
                         lambda s: s.update(artwork_sha256={}),
                         lambda s: s.update(boot_id="live-boot")):
            state = copy.deepcopy(self.state)
            mutation(state)
            with self.assertRaises(RuntimeError):
                self.admit(state)


if __name__ == "__main__":
    unittest.main()
