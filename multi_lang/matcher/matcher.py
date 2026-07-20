import os, json
from http.server import BaseHTTPRequestHandler, HTTPServer

class Matcher(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers['Content-Length'])
        jobs = json.loads(self.rfile.read(length))
        
        # Optional AI usage isolated here (e.g., Groq, OpenRouter)
        api_key = os.getenv("GROQ_API_KEY")
        for j in jobs:
            j['score'] = 99 if api_key else 50
            
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps(jobs).encode('utf-8'))

if __name__ == '__main__':
    HTTPServer(('', 8083), Matcher).serve_forever()
