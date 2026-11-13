from pathlib import Path
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


class TrackedFileContractTests(unittest.TestCase):
    def test_no_compiled_python_is_tracked(self) -> None:
        # Python imports a cached .pyc in place of the .py beside it, and a
        # hash-based "unchecked" one is never compared with that source. A
        # tracked .pyc would let BuildStream run plugin code no diff shows.
        if shutil.which("git") is None or not (ROOT / ".git").exists():
            self.skipTest("not a git checkout")

        tracked = subprocess.run(
            ["git", "ls-files", "-z", "--", "*.pyc", "*.pyo"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout

        self.assertEqual([path for path in tracked.split("\0") if path], [])


if __name__ == "__main__":
    unittest.main()
