import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from scrapers.manager import ScraperManager  # noqa: E402


class ActiveFleetTest(unittest.TestCase):
    def test_active_fleet_is_only_the_reliable_engines(self):
        names = [s.name for s in ScraperManager().default_scrapers]
        self.assertEqual(names, ["LinkedIn", "Glassdoor", "Apify Cloud"])


if __name__ == "__main__":
    unittest.main()
