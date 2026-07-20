import re
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

class Parser(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers['Content-Length'])
        resume_text = self.rfile.read(length).decode('utf-8')
        
        # Local rule-based parsing
        skills_keywords = ['python', 'java', 'react', 'go', 'rust', 'c#', 'sql', 'aws', 'docker']
        found_skills = [s for s in skills_keywords if s in resume_text.lower()]
        
        years_match = re.search(r'(\d+)\+?\s*years? of experience', resume_text, re.IGNORECASE)
        years_exp = int(years_match.group(1)) if years_match else 0
        
        result = {
            "skills": found_skills,
            "years_of_experience": years_exp,
            "is_ai_parsed": False
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))

if __name__ == '__main__':
    print("Starting Local Resume Parser on :8084")
    HTTPServer(('', 8084), Parser).serve_forever()
