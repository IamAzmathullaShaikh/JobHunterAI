import io
import json
import sys
import os
import unittest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from scripts import scrape_cli  # noqa: E402


class SerializeTest(unittest.TestCase):
    def test_serialize_converts_date_posted_to_iso(self):
        class Fake:
            def model_dump(self):
                return {"title": "X", "date_posted": datetime(2026, 7, 21, 9, 0, 0)}
        out = scrape_cli._serialize(Fake())
        self.assertEqual(out["date_posted"], "2026-07-21T09:00:00")

    def test_serialize_handles_none_date(self):
        class Fake:
            def model_dump(self):
                return {"title": "X", "date_posted": None}
        out = scrape_cli._serialize(Fake())
        self.assertIsNone(out["date_posted"])


class MainEmptyQueryTest(unittest.TestCase):
    def test_empty_query_prints_empty_array_without_scraping(self):
        old_in, old_out = sys.stdin, sys.stdout
        sys.stdin = io.StringIO(json.dumps({"search_query": ""}))
        sys.stdout = io.StringIO()
        try:
            scrape_cli.main()
            printed = sys.stdout.getvalue()
        finally:
            sys.stdin, sys.stdout = old_in, old_out
        self.assertEqual(json.loads(printed), [])


if __name__ == "__main__":
    unittest.main()
