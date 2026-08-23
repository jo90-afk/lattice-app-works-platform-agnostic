#!/usr/bin/env python3
"""Local, read-only human control surface for Lattice."""

from __future__ import annotations

import argparse
import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from control_plane import read_model
from state_engine import LatticeError, StateStore


ROOT = Path(__file__).resolve().parents[1]


def render_html(model: dict) -> str:
    projects = []
    for item in model["projects"]:
        project = item["project"]
        objective = item["objective"]
        milestone = item["milestone"]
        frontier = item["frontier"]
        leases = item["active_leases"]
        verification = item["pending_verification"]
        exceptions = item["open_exceptions"]
        def rows(values, primary, secondary):
            if not values:
                return "<li class='empty'>None</li>"
            return "".join(f"<li><strong>{html.escape(str(primary(v)))}</strong><span>{html.escape(str(secondary(v)))}</span></li>" for v in values)
        projects.append(f"""
<section class='project'><header><div><p class='eyebrow'>{html.escape(project['status'])}</p><h2>{html.escape(project['name'])}</h2></div><code>{html.escape(project['id'])}</code></header>
<div class='current'><div><span>Objective</span><strong>{html.escape(objective['title']) if objective else 'None active'}</strong></div><div><span>Milestone</span><strong>{html.escape(milestone['title']) if milestone else 'None active'}</strong></div></div>
<div class='grid'>
<article><h3>Ready now <b>{len(frontier)}</b></h3><ul>{rows(frontier, lambda x:x['title'], lambda x:f"{x['role']} · {x['kind']}")}</ul></article>
<article><h3>In flight <b>{len(leases)}</b></h3><ul>{rows(leases, lambda x:x['leased_by'], lambda x:f"{x['role']} · until {x['expires_at']}")}</ul></article>
<article><h3>Verification <b>{len(verification)}</b></h3><ul>{rows(verification, lambda x:x['title'], lambda x:f"waiting for {x['verifier_role']}")}</ul></article>
<article class='exceptions'><h3>Exceptions <b>{len(exceptions)}</b></h3><ul>{rows(exceptions, lambda x:x['title'], lambda x:f"{x['severity']} · {x['owner_role']}")}</ul></article>
</div></section>""")
    body = "".join(projects) or "<p>No projects are registered.</p>"
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Lattice Control Plane</title><style>
:root{{color-scheme:dark;font-family:Inter,ui-sans-serif,system-ui,sans-serif;background:#111;color:#eee}}*{{box-sizing:border-box}}body{{margin:0;background:#111;color:#eee}}main{{max-width:1180px;margin:auto;padding:40px 24px 80px}}h1{{font-size:clamp(2rem,5vw,4.5rem);letter-spacing:-.06em;margin:.1em 0}}.lede{{color:#aaa;max-width:720px;line-height:1.5}}.top{{display:flex;justify-content:space-between;gap:24px;align-items:flex-end;margin-bottom:48px}}.revision,code{{font-family:ui-monospace,monospace;color:#999}}.project{{border-top:1px solid #444;padding:28px 0 36px}}.project header{{display:flex;justify-content:space-between;gap:20px}}h2{{font-size:2rem;margin:0}}.eyebrow{{text-transform:uppercase;font-size:.7rem;letter-spacing:.14em;color:#999;margin:0 0 7px}}.current{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:28px 0}}.current div,article{{background:#181818;border:1px solid #2b2b2b;border-radius:10px;padding:18px}}.current span{{display:block;color:#888;font-size:.75rem;text-transform:uppercase;letter-spacing:.1em;margin-bottom:7px}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}article{{min-height:180px}}h3{{margin:0 0 14px;font-size:.9rem;text-transform:uppercase;letter-spacing:.08em;color:#aaa;display:flex;justify-content:space-between}}ul{{list-style:none;padding:0;margin:0}}li{{padding:10px 0;border-top:1px solid #2b2b2b}}li:first-child{{border-top:0}}li strong,li span{{display:block}}li span{{font-size:.78rem;color:#888;margin-top:4px}}.empty{{color:#777}}.exceptions{{border-color:#473333}}@media(max-width:850px){{.grid{{grid-template-columns:1fr 1fr}}}}@media(max-width:560px){{main{{padding:24px 16px 56px}}.top{{display:block}}.current,.grid{{grid-template-columns:1fr}}}}
</style></head><body><main><div class='top'><div><p class='eyebrow'>Local control surface</p><h1>Lattice</h1><p class='lede'>Current project state, derived work, verification, and exceptions. This surface is read-only; authority remains in the guarded state engine.</p></div><div class='revision'>revision {model['revision']}</div></div>{body}</main></body></html>"""


class ControlHandler(BaseHTTPRequestHandler):
    server_version = "LatticeControl/0.0.5"
    def _model(self) -> dict:
        query = parse_qs(urlparse(self.path).query)
        with StateStore(ROOT) as store:
            return read_model(store, query.get("project", [None])[0], 5)
    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/api/state":
                payload = json.dumps(self._model(), indent=2, sort_keys=True).encode(); status=200; content_type="application/json; charset=utf-8"
            elif parsed.path in {"/", "/index.html"}:
                payload = render_html(self._model()).encode(); status=200; content_type="text/html; charset=utf-8"
            elif parsed.path == "/health":
                payload=b'{"ok":true}\n'; status=200; content_type="application/json; charset=utf-8"
            else:
                payload=b"Not found\n"; status=404; content_type="text/plain; charset=utf-8"
        except LatticeError as error:
            payload=json.dumps({"error":str(error)}).encode(); status=400; content_type="application/json; charset=utf-8"
        self.send_response(status); self.send_header("Content-Type", content_type); self.send_header("Cache-Control", "no-store"); self.send_header("Content-Length", str(len(payload))); self.end_headers(); self.wfile.write(payload)
    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> int:
    parser=argparse.ArgumentParser(description="Serve Lattice's local read-only control surface."); parser.add_argument("--host", default="127.0.0.1"); parser.add_argument("--port", type=int, default=8765); args=parser.parse_args()
    server=ThreadingHTTPServer((args.host,args.port),ControlHandler); print(f"Lattice control surface: http://{args.host}:{args.port}")
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
