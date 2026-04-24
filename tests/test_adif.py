import os
import tempfile
import unittest

from src.adif import ADIFParser, export_contacts_to_adif, validate_adif_file


class ADIFParserTests(unittest.TestCase):
    def test_field_data_can_contain_angle_brackets(self):
        parser = ADIFParser()

        contact = parser._parse_record(
            "<CALL:6>N0CALL "
            "<COMMENT:18>A<B marker here ok "
            "<QSO_DATE:8>20260424 "
            "<TIME_ON:4>1200 "
            "<EOR>"
        )

        self.assertEqual(contact["callsign"], "N0CALL")
        self.assertEqual(contact["comment"], "A<B marker here ok")
        self.assertEqual(contact["date"], "2026-04-24")
        self.assertEqual(contact["time_on"], "12:00")

    def test_validation_accepts_headerless_adif_record(self):
        with tempfile.NamedTemporaryFile("w", suffix=".adi", delete=False) as handle:
            handle.write("<CALL:6>N0CALL <QSO_DATE:8>20260424 <TIME_ON:4>1200 <EOR>")
            path = handle.name

        try:
            is_valid, message = validate_adif_file(path)
        finally:
            os.unlink(path)

        self.assertTrue(is_valid, message)


class ADIFGeneratorTests(unittest.TestCase):
    def test_exports_standard_and_app_dxcc_entity_fields(self):
        with tempfile.NamedTemporaryFile("r", suffix=".adi", delete=False) as handle:
            path = handle.name

        try:
            export_contacts_to_adif(
                [
                    {
                        "callsign": "N0CALL",
                        "date": "2026-04-24",
                        "time_on": "12:00",
                        "band": "20m",
                        "mode": "CW",
                        "dxcc_entity": 291,
                    }
                ],
                path,
            )

            with open(path, encoding="utf-8") as handle:
                content = handle.read()
        finally:
            os.unlink(path)

        self.assertIn("<DXCC:3>291", content)
        self.assertIn("<DXCC_ENTITY:3>291", content)


if __name__ == "__main__":
    unittest.main()
