import unittest
import requests
import json
import time

class TestUrlConsistency(unittest.TestCase):
    def setUp(self):
        # We assume the app is running on localhost:3000
        self.base_url = "http://localhost:3000"

    def test_job_url_consistency(self):
        # Trigger scraper
        payload = {
            "search_query": "React Developer",
            "location": "Remote",
            "job_type": "Full-Time"
        }
        resp = requests.post(f"{self.base_url}/api/scrape", json=payload)
        self.assertEqual(resp.status_code, 200, "Scraper endpoint should return 200")
        
        data = resp.json()
        jobs = data.get("jobs", [])
        self.assertGreater(len(jobs), 0, "Should have scraped some jobs")
        
        # Check first job consistency
        job = jobs[-1]
        
        raw_url = job.get("raw_url", "")
        canonical_url = job.get("canonical_url", "")
        needs_validation = job.get("needs_validation", False)
        
        # Output DB info
        print(f"\nLOG_DB_TEST: {job['id']} {job['title']} raw: {raw_url} canonical: {canonical_url} needs_val: {needs_validation}")
        
        self.assertIsNotNone(raw_url, "raw_url must exist")
        
        if needs_validation:
            self.assertEqual(canonical_url, "", "canonical_url should be empty if needs validation")
        else:
            self.assertNotEqual(canonical_url, "", "canonical_url should exist if valid")

if __name__ == '__main__':
    unittest.main()
