"""Local dev server for the extraction API.

Vercel runs api/extract.py as a serverless Python function in production, but
`next dev` cannot. This tiny stdlib server exposes the same run_extraction()
on http://127.0.0.1:8000/api/extract, and next.config.ts proxies to it in
development. Not deployed; local convenience only.

    GROQ_API_KEY=... python devserver.py
    # (run with an environment that has `belegradar` installed)
"""

from __future__ import annotations

import importlib.util
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

_spec = importlib.util.spec_from_file_location(
    "extract_fn", os.path.join(os.path.dirname(__file__), "api", "extract.py")
)
_fn = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fn)


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else b""
        status, payload = _fn.run_extraction(body)
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass  # quiet


if __name__ == "__main__":
    print("belegradar dev API on http://127.0.0.1:8000/api/extract")
    HTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
