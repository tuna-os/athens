from pathlib import Path
import re
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
ELEMENTS = ROOT / "elements"

# A local element reference is a path ending in .bst. In a junction-qualified
# name such as `gnome-build-meta.bst:core/foo.bst`, only the part before the
# first colon is an element of this project.
ELEMENT_REF = re.compile(r"[A-Za-z0-9_./-]+\.bst(?::[A-Za-z0-9_./:-]+\.bst)?")


def local_refs(text: str) -> set[str]:
    return {match.split(":", 1)[0] for match in ELEMENT_REF.findall(text)}


class ElementGraphTests(unittest.TestCase):
    def test_every_element_is_reachable_from_a_build_entry_point(self) -> None:
        # Builds and CI only load the elements their targets depend on. An
        # element no target reaches is never built or validated, so it can rot
        # unnoticed while still looking like part of the image.
        if shutil.which("git") is None or not (ROOT / ".git").exists():
            self.skipTest("not a git checkout")

        tracked = [
            Path(path)
            for path in subprocess.run(
                ["git", "ls-files", "-z"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.split("\0")
            if path
        ]
        elements = {
            path.relative_to("elements").as_posix()
            for path in tracked
            if path.parts[0] == "elements" and path.suffix == ".bst"
        }

        # Entry points: everything outside elements/ that names an element
        # (project.conf, mkosi configuration, the Justfile, CI workflows,
        # scripts), except these tests, which only describe the graph.
        reachable: set[str] = set()
        for path in tracked:
            if path.parts[0] in ("elements", "tests"):
                continue
            try:
                text = (ROOT / path).read_text(encoding="utf-8")
            except (UnicodeDecodeError, IsADirectoryError):
                continue
            reachable |= local_refs(text) & elements

        pending = list(reachable)
        while pending:
            text = (ELEMENTS / pending.pop()).read_text(encoding="utf-8")
            for ref in local_refs(text) & elements:
                if ref not in reachable:
                    reachable.add(ref)
                    pending.append(ref)

        self.assertTrue(reachable)
        self.assertEqual(sorted(elements - reachable), [])


if __name__ == "__main__":
    unittest.main()
