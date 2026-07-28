import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_path_traversal_blocked():
    """Verify that path traversal attempts are blocked."""
    # 1. Invalid pattern
    resp = client.get("/api/resumes/download/malicious.txt")
    assert resp.status_code == 400
    assert "Invalid file access pattern" in resp.json()["detail"]

    # 2. Path Traversal attempt
    resp2 = client.get("/api/resumes/download/export_..%2f..%2f..%2f.env")
    # Starlette/FastAPI will return 404 because the %2f doesn't match the path param segment
    assert resp2.status_code in [403, 404]

def test_valid_file_not_found():
    """Verify that a valid pattern for a non-existent file returns 404."""
    resp = client.get("/api/resumes/download/export_99999.pdf")
    assert resp.status_code == 404
