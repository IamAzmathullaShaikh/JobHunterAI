import os, json
from http.server import BaseHTTPRequestHandler, HTTPServer

class AIMatcher(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers['Content-Length'])
        payload = json.loads(self.rfile.read(length).decode('utf-8'))
        jobs = payload.get('jobs', [])
        
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            self.send_response(503)
            self.end_headers()
            self.wfile.write(b'{"error": "AI not configured. Use local matcher."}')
            return
            
        # Mock AI usage
        for j in jobs:
            j['ai_semantic_score'] = 95
            
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(jobs).encode('utf-8'))

if __name__ == '__main__':
    print("Starting Optional AI Matcher on :8086")
    HTTPServer(('', 8086), AIMatcher).serve_forever()
