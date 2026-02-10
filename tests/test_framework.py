import json
import tempfile
import unittest
from pathlib import Path

from dq_framework import run_framework


class FrameworkSmokeTest(unittest.TestCase):
    def test_end_to_end_csv(self):
        with tempfile.TemporaryDirectory() as td:
            result = run_framework("sample_data/retail_orders_sample.csv", output_dir=td)
            self.assertIn("summary", result)
            self.assertIn("artifacts", result)
            self.assertIn(result["summary"]["go_caution_no_go"], {"GO", "CAUTION", "NO-GO"})
            metrics_path = Path(result["artifacts"]["metrics_json"])
            self.assertTrue(metrics_path.exists())
            data = json.loads(metrics_path.read_text())
            self.assertIn("dimensions", data)
            self.assertIn("accuracy", data["dimensions"])


if __name__ == "__main__":
    unittest.main()
