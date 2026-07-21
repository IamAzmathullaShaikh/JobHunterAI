import sys, json
params = json.loads(sys.stdin.read() or "{}")
sys.stderr.write("stub log line\n")
print(json.dumps([{
    "job_id_raw": "stub-1",
    "title": "Stub Engineer " + params.get("search_query", ""),
    "company_name": "StubCo",
    "location": params.get("location", "Remote"),
    "work_place_type": "Remote",
    "job_type": params.get("job_type", "Full-Time"),
    "source": "LinkedIn",
    "url": "https://example.com/jobs/stub-1",
    "description_raw": "desc",
    "date_posted": None
}]))
