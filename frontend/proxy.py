"""Local dev proxy — serves frontend + proxies /api/* to api.synup.com.

Usage:
    python proxy.py
    # Open http://localhost:8080
"""

import http.server
import urllib.request
import os

PORT = 8080
API_BASE = "https://api.synup.com/api/v4"
FRONTEND_DIR = os.path.dirname(os.path.abspath(__file__))


class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def do_GET(self):
        if self.path.startswith("/api/"):
            self._proxy("GET")
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/"):
            self._proxy("POST")
        else:
            self.send_error(405)

    def _proxy(self, method):
        # Strip /api prefix → forward to api.synup.com/api/v4/...
        remote_path = self.path[len("/api"):]  # keeps the /v4/... part
        url = f"https://api.synup.com/api{remote_path}"

        # Forward headers
        headers = {}
        for key in ("Authorization", "Content-Type"):
            val = self.headers.get(key)
            if val:
                headers[key] = val

        # Read body for POST
        body = None
        if method == "POST":
            length = int(self.headers.get("Content-Length", 0))
            if length:
                body = self.rfile.read(length)

        req = urllib.request.Request(url, data=body, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req) as resp:
                resp_body = resp.read()
                self.send_response(resp.status)
                self.send_header("Content-Type", resp.headers.get("Content-Type", "application/json"))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(resp_body)
        except urllib.error.HTTPError as e:
            resp_body = e.read()
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(resp_body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.end_headers()


if __name__ == "__main__":
    server = http.server.HTTPServer(("", PORT), ProxyHandler)
    print(f"Serving frontend + API proxy on http://localhost:{PORT}")
    server.serve_forever()
