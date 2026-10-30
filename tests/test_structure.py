"""Guards for brief rules that would otherwise fail silently.

1. No banned libraries (pandas, NumPy, scikit-learn, heapq) in the project code.
2. No sorted() or .sort() in the project code, except measure.py, which verifies output.
3. config.py settings meet the brief's minimums.
4. Required files are present.
"""
import ast
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CODE = [REPO / "main.py", *sorted((REPO / "src").glob("*.py"))]
BANNED_MODULES = {"pandas", "numpy", "sklearn", "scipy", "heapq"}
SORTED_ALLOWED = {"measure.py"}


def _tree(path):
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


class TestLibraryRules(unittest.TestCase):
    def test_no_banned_imports(self):
        found = []
        for path in CODE:
            for node in ast.walk(_tree(path)):
                names = []
                if isinstance(node, ast.Import):
                    names = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    names = [node.module]
                found += [f"{path.name}: {n}" for n in names if n.split(".")[0] in BANNED_MODULES]
        self.assertEqual(found, [], f"banned imports: {found}")

    def test_no_builtin_sorting(self):
        found = []
        for path in CODE:
            if path.name in SORTED_ALLOWED:
                continue
            for node in ast.walk(_tree(path)):
                if isinstance(node, ast.Call):
                    f = node.func
                    if (isinstance(f, ast.Name) and f.id == "sorted") or (
                        isinstance(f, ast.Attribute) and f.attr == "sort"
                    ):
                        found.append(f"{path.name}, line {node.lineno}")
        self.assertEqual(found, [], f"sorted() or .sort() used: {found}")


class TestConfig(unittest.TestCase):
    def test_settings_meet_brief(self):
        from src import config
        self.assertTrue({5, 10, 20} <= set(config.SCALING_SIZES))
        self.assertGreaterEqual(config.ORDER_N, 1000)
        self.assertGreaterEqual(config.REPEATS, 5)
        self.assertEqual(config.SCALING_COLUMN, "median_income")


class TestFiles(unittest.TestCase):
    def test_required_files(self):
        for name in ("README.md", "housing.csv", "main.py", "src/config.py", "src/sorts.py"):
            with self.subTest(file=name):
                self.assertTrue((REPO / name).exists(), f"{name} is missing")


if __name__ == "__main__":
    unittest.main()
