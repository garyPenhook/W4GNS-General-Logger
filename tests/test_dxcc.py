import ast
import pathlib
import unittest

from src.dxcc import lookup_dxcc


class DXCCLookupTests(unittest.TestCase):
    def test_dxcc_data_has_no_duplicate_literal_keys(self):
        dxcc_path = pathlib.Path(__file__).resolve().parents[1] / "src" / "dxcc.py"
        tree = ast.parse(dxcc_path.read_text(encoding="utf-8"), filename=str(dxcc_path))

        duplicates = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            if not any(isinstance(target, ast.Name) and target.id == "DXCC_DATA" for target in node.targets):
                continue
            if not isinstance(node.value, ast.Dict):
                continue

            seen = {}
            for key in node.value.keys:
                if isinstance(key, ast.Constant):
                    if key.value in seen:
                        duplicates.append((key.value, seen[key.value], key.lineno))
                    else:
                        seen[key.value] = key.lineno

        self.assertEqual(duplicates, [])

    def test_s2_prefix_resolves_to_bangladesh(self):
        self.assertEqual(lookup_dxcc("S21ABC")["country"], "Bangladesh")

    def test_9v_prefix_resolves_to_singapore(self):
        self.assertEqual(lookup_dxcc("9V1ABC")["country"], "Singapore")


if __name__ == "__main__":
    unittest.main()
