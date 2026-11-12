"""Tiny static-file helpers with HTTP Range support (needed for seeking inside audio and video)."""
from __future__ import annotations

import http.server
import mimetypes
import re
from pathlib import Path

mimetypes.add_type("audio/wav", ".wav")
mimetypes.add_type("audio/flac", ".flac")
mimetypes.add_type("text/vtt", ".vtt")


def safe_join(base: Path, rel: str) -> Path | None:
    """Resolve `rel` under `base`; return None when it would escape or does not exist as a file."""
    base = base.resolve()
    target = (base / rel.lstrip("/")).resolve()
    if base != target and base not in target.parents:
        return None
    return target if target.is_file() else None


def send_file(h: http.server.BaseHTTPRequestHandler, path: Path, head_only: bool = False) -> None:
    size = path.stat().st_size
    ctype = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    start, end, status = 0, size - 1, 200
    m = re.match(r"bytes=(\d*)-(\d*)$", h.headers.get("Range", "").strip())
    if m and (m.group(1) or m.group(2)):
        if m.group(1):
            start = int(m.group(1))
            end = int(m.group(2)) if m.group(2) else size - 1
        else:  # suffix range: last N bytes
            start = max(0, size - int(m.group(2)))
        end = min(end, size - 1)
        if start > end or start >= size:
            h.send_response(416)
            h.send_header("Content-Range", f"bytes */{size}")
            h.end_headers()
            return
        status = 206
    h.send_response(status)
    h.send_header("Content-Type", ctype)
    h.send_header("Accept-Ranges", "bytes")
    h.send_header("Content-Length", str(end - start + 1))
    h.send_header("Cache-Control", "no-store")
    if status == 206:
        h.send_header("Content-Range", f"bytes {start}-{end}/{size}")
    h.end_headers()
    if head_only:
        return
    with open(path, "rb") as fh:
        fh.seek(start)
        left = end - start + 1
        while left > 0:
            chunk = fh.read(min(1 << 16, left))
            if not chunk:
                break
            try:
                h.wfile.write(chunk)
            except (BrokenPipeError, ConnectionResetError):
                return
            left -= len(chunk)


def static_handler(directory: Path):
    """Handler class serving `directory` read-only, loopback use only, with Range support."""
    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a):  # quiet
            pass

        def _serve(self, head_only):
            rel = self.path.split("?", 1)[0].split("#", 1)[0]
            rel = "index.html" if rel in ("", "/") else re.sub(r"%([0-9a-fA-F]{2})", lambda m: chr(int(m.group(1), 16)), rel)
            target = safe_join(directory, rel)
            if not target:
                self.send_error(404)
                return
            send_file(self, target, head_only)

        def do_GET(self):
            self._serve(False)

        def do_HEAD(self):
            self._serve(True)
    return Handler
