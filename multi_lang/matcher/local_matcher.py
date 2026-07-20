import json
from http.server import BaseHTTPRequestHandler, HTTPServer

class LocalMatcher(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers['Content-Length'])
        payload = json.loads(self.rfile.read(length).decode('utf-8'))
        
        jobs = payload.get('jobs', [])
        resume_skills = set(payload.get('resume', {}).get('skills', []))
        
        for job in jobs:
            desc = job.get('description', '').lower()
            job_skills = set([s for s in resume_skills if s in desc])
            # Simple Jaccard-like similarity or match count
            match_score = len(job_skills) * 10 
            job['local_match_score'] = min(match_score, 100)
            job['matched_skills'] = list(job_skills)
            
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(jobs).encode('utf-8'))

if __name__ == '__main__':
    print("Starting Local Matcher on :8085")
    HTTPServer(('', 8085), LocalMatcher).serve_forever()
