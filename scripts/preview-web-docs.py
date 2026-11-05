#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#
# ]
# ///


import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


import http.server
import socketserver

PORT = 8000
DIRECTORY = REPO_ROOT / "docs"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
    print(f"preview at http://127.0.0.1:{PORT}")
    httpd.serve_forever()
