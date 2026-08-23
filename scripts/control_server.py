#!/usr/bin/env python3
"""Local, read-only human control surface for Lattice."""

from __future__ import annotations

import argparse
import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from state_engine import LatticeError
from store_factory import open_state_store
from supervision_model import supervision_model

ROOT = Path(__file__).resolve().parents[1]


def _rows(values, primary, secondary):
    if not values:
        return "<li class='empty'>None</li>"
    return "".join(
        f"<li><strong>{html.escape(str(primary(v)))}</strong><span>{html.escape(str(secondary(v)))}</span></li>"
        for v in values
    )


def _metric(label: str, value: object) -> str:
    return f"<div class='metric'><span>{html.escape(label)}</span><strong>{html.escape(str(value))}</strong></div>"


def _duration(seconds: int | None) -> str:
    if seconds is None:
        return "—"
    seconds = max(0, int(seconds))
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    if hours < 48:
        return f"{hours}h {minutes % 60}m"
    days = hours // 24
    return f"{days}d {hours % 24}h"


def _change_label(change: dict) -> str:
    labels = {
        "milestone_accepted": "Milestone accepted",
        "submission_reviewed": "Verification recorded",
        "truth_recorded": "Truth recorded",
        "truth_revised": "Truth revised",
        "truth_attention_changed": "Truth attention changed",
        "record_created": "Record created",
        "record_revised": "Record revised",
        "condition_added": "Condition added",
        "condition_submitted": "Condition submitted",
        "commitment_fulfilled": "Commitment fulfilled",
        "exception_resolved": "Exception resolved",
    }
    return labels.get(change["event_type"], change["event_type"].replace("_", " ").title())


def _decision_cards(items: list[dict]) -> str:
    if not items:
        return "<p class='empty'>No Principal decision required.</p>"
    cards = []
    for item in items:
        affected = item.get("affected_state") or {}
        objective = affected.get("active_objective") or {}
        milestone = affected.get("active_milestone") or {}
        target = affected.get("target") or {}
        target_state = target.get("state") or {}
        target_summary = target_state.get("title") or target_state.get("key") or target.get("id") or "No specific target"
        evidence = item.get("evidence") or []
        evidence_rows = _rows(
            evidence,
            lambda x: x.get("summary") or x.get("entity_id"),
            lambda x: " · ".join(part for part in [x.get("role"), x.get("source_ref")] if part),
        ) if evidence else "<li class='empty'>No durable evidence attached to this decision target.</li>"
        choices = "".join(
            "<div class='choice'><strong>" + html.escape(choice["label"]) + "</strong><p>" + html.escape(choice["consequence"]) + "</p></div>"
            for choice in item.get("supported_choices", [])
        )
        cards.append(f"""
<article class='decision-card'>
<div class='decision-title'><div><p class='eyebrow'>{html.escape(item['kind'])} · {html.escape(item['project_id'])}</p><h3>{html.escape(item['decision_required'])}</h3></div><span class='decision-state'>{'blocking' if item.get('blocking') else 'open'}</span></div>
<p class='detail'>{html.escape(item.get('detail') or '')}</p>
<div class='why'><strong>Why this reached the Principal</strong><p>{html.escape(item['authority_reason'])}</p></div>
<div class='decision-context'><div><span>Active objective</span><strong>{html.escape(str(objective.get('title') or 'None active'))}</strong></div><div><span>Active milestone</span><strong>{html.escape(str(milestone.get('title') or 'None active'))}</strong></div><div><span>Affected target</span><strong>{html.escape(str(target_summary))}</strong></div><div><span>Semantic revision</span><strong>{html.escape(str(affected.get('semantic_revision', '—')))}</strong></div></div>
<div class='decision-lower'><div><h4>Available evidence</h4><ul>{evidence_rows}</ul></div><div><h4>Supported choices and consequences</h4>{choices}</div></div>
</article>""")
    return "".join(cards)


def _graph_html(graph: dict) -> str:
    nodes = {node["id"]: node for node in graph.get("nodes", [])}
    counts = graph.get("counts", {})
    count_badges = "".join(
        f"<span class='graph-count'><b>{html.escape(str(count))}</b> {html.escape(kind)}</span>"
        for kind, count in counts.items() if count
    ) or "<span class='empty'>No linked consequence state.</span>"
    relations = []
    for edge in graph.get("edges", []):
        source = nodes.get(edge["source"], {"label": edge["source"], "type": "unknown"})
        target = nodes.get(edge["target"], {"label": edge["target"], "type": "unknown"})
        relations.append(
            "<li class='graph-edge'>"
            f"<span class='graph-node'><i>{html.escape(source['type'])}</i>{html.escape(str(source['label']))}</span>"
            f"<span class='graph-relation'>{html.escape(edge['relation'].replace('_', ' '))}</span>"
            f"<span class='graph-node'><i>{html.escape(target['type'])}</i>{html.escape(str(target['label']))}</span>"
            "</li>"
        )
    relation_html = "".join(relations) or "<li class='empty'>No consequence relationships in the active objective.</li>"
    return f"""
<article class='consequence'>
<div class='consequence-head'><div><h3>Consequence graph</h3><p class='detail'>Durable state and derived work, shown as explicit relationships rather than a document tree.</p></div><div class='graph-counts'>{count_badges}</div></div>
<ul class='graph-edges'>{relation_html}</ul>
</article>"""


def render_html(model: dict) -> str:
    inbox = model.get("principal_inbox") or {"count": 0, "blocking_count": 0, "items": []}
    portfolio = model.get("portfolio") or {}
    telemetry = model.get("operational_telemetry") or {}
    backend = model.get("state_backend", "sqlite")
    decision_cards = _decision_cards(inbox.get("items", []))

    changes = model.get("recent_accepted_changes") or []
    change_rows = _rows(
        changes,
        _change_label,
        lambda x: f"{x['project_id']} · {x['role']} · r{x['revision']} · {x['created_at']}",
    ) if changes else "<li class='empty'>No accepted changes recorded yet.</li>"

    projects = []
    for item in model["projects"]:
        project = item["project"]
        objective = item["objective"]
        milestone = item["milestone"]
        frontier = item["frontier"]
        leases = item["active_leases"]
        verification = item["pending_verification"]
        exceptions = item["open_exceptions"]
        temporal = item.get("temporal_health") or {}
        blocked = temporal.get("blocked_conditions") or []
        readiness = item.get("readiness") or {}
        evidence = item.get("evidence_chain") or []
        truths = item.get("frontier_truths") or []
        ready_label = "ready" if readiness.get("ready") else "not ready"
        readiness_detail = readiness.get("reason") or readiness.get("summary") or "Derived from current milestone predicates."
        evidence_rows = _rows(
            evidence,
            lambda x: x.get("condition_title") or x.get("summary") or x.get("entity_id"),
            lambda x: " · ".join(part for part in [x.get("entity_type"), x.get("role"), x.get("review_verdict"), x.get("source_ref")] if part),
        )
        projects.append(f"""
<section class='project'><header><div><p class='eyebrow'>{html.escape(project['status'])}</p><h2>{html.escape(project['name'])}</h2></div><div class='project-meta'><code>{html.escape(project['id'])}</code><span>semantic r{item['semantic_revision']}</span></div></header>
<div class='current'><div><span>Objective</span><strong>{html.escape(objective['title']) if objective else 'None active'}</strong></div><div><span>Milestone</span><strong>{html.escape(milestone['title']) if milestone else 'None active'}</strong></div></div>
<div class='grid'>
<article><h3>Ready now <b>{len(frontier)}</b></h3><ul>{_rows(frontier, lambda x:x['title'], lambda x:f"{x['role']} · {x['kind']}")}</ul></article>
<article><h3>In flight <b>{len(leases)}</b></h3><ul>{_rows(leases, lambda x:x['leased_by'], lambda x:f"{x['role']} · active {_duration(x.get('age_seconds'))} · lease {_duration(max(0, x.get('remaining_seconds', 0)))} remaining")}</ul></article>
<article><h3>Verification <b>{len(verification)}</b></h3><ul>{_rows(verification, lambda x:x['title'], lambda x:f"waiting for {x['verifier_role']} · {_duration(x.get('waiting_seconds'))}")}</ul></article>
<article class='exceptions'><h3>Exceptions <b>{len(exceptions)}</b></h3><ul>{_rows(exceptions, lambda x:x['title'], lambda x:f"{x['severity']} · {x['owner_role']} · open {_duration(x.get('open_seconds'))}")}</ul></article>
</div>
<div class='health-strip'><span>Oldest attention <b>{_duration(temporal.get('oldest_attention_seconds'))}</b></span><span>Oldest verification <b>{_duration(temporal.get('oldest_verification_wait_seconds'))}</b></span><span>Blocked conditions <b>{len(blocked)}</b></span></div>
<div class='evidence-grid'>
<article><h3>Milestone readiness <b>{html.escape(ready_label)}</b></h3><p class='detail'>{html.escape(str(readiness_detail))}</p><h3 class='subhead'>Blocked conditions <b>{len(blocked)}</b></h3><ul>{_rows(blocked, lambda x:x['title'], lambda x:f"{x['owner_role']} · blocked {_duration(x.get('blocked_seconds'))} · attempts {x['attempt_count']}/{x['attempt_budget']}")}</ul><h3 class='subhead'>Frontier truths <b>{len(truths)}</b></h3><ul>{_rows(truths, lambda x:x['statement'], lambda x:f"{x['epistemic_status']} · v{x['version']}")}</ul></article>
<article><h3>Evidence chain <b>{len(evidence)}</b></h3><ul>{evidence_rows}</ul></article>
</div>{_graph_html(item.get('consequence_graph') or {})}</section>""")
    body = "".join(projects) or "<p>No projects are registered.</p>"

    metrics = "".join([
        _metric("Active projects", portfolio.get("active_projects", 0)),
        _metric("Ready actions", portfolio.get("ready_actions", 0)),
        _metric("In flight", portfolio.get("in_flight", 0)),
        _metric("Verification", portfolio.get("pending_verification", 0)),
        _metric("Exceptions", portfolio.get("open_exceptions", 0)),
        _metric("Oldest attention", _duration(portfolio.get("oldest_attention_seconds"))),
    ])
    failure_rate = telemetry.get("verification_failure_rate")
    telemetry_metrics = "".join([
        _metric("Median action", _duration(telemetry.get("median_action_duration_seconds"))),
        _metric("Longest action", _duration(telemetry.get("max_action_duration_seconds"))),
        _metric("Retries", telemetry.get("retries", 0)),
        _metric("Recoveries", telemetry.get("recoveries", 0)),
        _metric("Verification failures", "—" if failure_rate is None else f"{failure_rate * 100:.0f}%"),
        _metric("Worker failures", telemetry.get("worker_failures", 0)),
        _metric("Exceptions raised", telemetry.get("exceptions_raised", 0)),
        _metric("Hook failures", telemetry.get("hook_failures", 0)),
    ])

    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Lattice Control Plane</title><style>
:root{{color-scheme:dark;font-family:Inter,ui-sans-serif,system-ui,sans-serif;background:#111;color:#eee}}*{{box-sizing:border-box}}body{{margin:0;background:#111;color:#eee}}main{{max-width:1220px;margin:auto;padding:40px 24px 80px}}h1{{font-size:clamp(2rem,5vw,4.5rem);letter-spacing:-.06em;margin:.1em 0}}.lede,.detail{{color:#aaa;line-height:1.5}}.top{{display:flex;justify-content:space-between;gap:24px;align-items:flex-end;margin-bottom:24px}}.revision,code{{font-family:ui-monospace,monospace;color:#999}}.system{{text-align:right}}.backend{{display:inline-block;border:1px solid #3b4a5b;background:#121820;border-radius:999px;padding:6px 10px;color:#9fb6cc;font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px}}.metrics{{display:grid;grid-template-columns:repeat(6,1fr);gap:8px;margin:0 0 28px}}.metric{{background:#181818;border:1px solid #2b2b2b;border-radius:9px;padding:14px}}.metric span,.project-meta span,.decision-context span{{display:block;color:#888;font-size:.7rem;text-transform:uppercase;letter-spacing:.08em}}.metric strong{{display:block;font-size:1.35rem;margin-top:5px}}.principal{{border:1px solid #5b4730;background:#19150f;border-radius:12px;padding:20px;margin:0 0 20px}}.principal>header{{display:flex;justify-content:space-between;align-items:center;gap:20px;margin-bottom:14px}}.principal h2{{font-size:1.2rem;margin:0}}.principal .count{{font-family:ui-monospace,monospace;color:#c7a36f}}.decision-card{{background:#15120e;border:1px solid #5b4730;min-height:0;margin-top:12px}}.decision-title{{display:flex;justify-content:space-between;gap:20px;align-items:flex-start}}.decision-title h3{{font-size:1.05rem;text-transform:none;letter-spacing:0;color:#eee;margin:0;display:block}}.decision-state{{font-size:.68rem;text-transform:uppercase;letter-spacing:.1em;border:1px solid #704a34;border-radius:999px;padding:5px 8px;color:#d8ad82}}.why{{border-left:2px solid #5b4730;padding-left:12px;margin:16px 0}}.why strong,.decision-lower h4{{font-size:.78rem;text-transform:uppercase;letter-spacing:.08em;color:#aaa}}.why p,.choice p{{color:#aaa;margin:5px 0 0;line-height:1.45;font-size:.86rem}}.decision-context{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:16px 0}}.decision-context div{{background:#1c1813;border-radius:7px;padding:10px}}.decision-context strong{{display:block;margin-top:5px;font-size:.84rem}}.decision-lower{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}.decision-lower h4{{margin:0 0 8px}}.choice{{border-top:1px solid #362b21;padding:9px 0}}.choice:first-of-type{{border-top:0}}.activity{{display:grid;grid-template-columns:2fr 1fr;gap:12px;margin-bottom:44px}}.activity>article{{min-height:0}}.telemetry{{display:grid;grid-template-columns:1fr 1fr;gap:7px}}.telemetry .metric{{padding:10px}}.project{{border-top:1px solid #444;padding:28px 0 36px}}.project header{{display:flex;justify-content:space-between;gap:20px}}.project-meta{{text-align:right}}h2{{font-size:2rem;margin:0}}.eyebrow{{text-transform:uppercase;font-size:.7rem;letter-spacing:.14em;color:#999;margin:0 0 7px}}.current{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:28px 0}}.current div,article{{background:#181818;border:1px solid #2b2b2b;border-radius:10px;padding:18px}}.current span{{display:block;color:#888;font-size:.75rem;text-transform:uppercase;letter-spacing:.1em;margin-bottom:7px}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}.health-strip{{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}}.health-strip span{{border:1px solid #2f2f2f;border-radius:999px;padding:7px 10px;color:#888;font-size:.76rem}}.health-strip b{{color:#ddd}}.evidence-grid{{display:grid;grid-template-columns:1fr 2fr;gap:12px;margin-top:12px}}article{{min-height:180px}}h3{{margin:0 0 14px;font-size:.9rem;text-transform:uppercase;letter-spacing:.08em;color:#aaa;display:flex;justify-content:space-between}}.subhead{{margin-top:22px}}ul{{list-style:none;padding:0;margin:0}}li{{padding:10px 0;border-top:1px solid #2b2b2b}}li:first-child{{border-top:0}}li strong,li span{{display:block}}li span{{font-size:.78rem;color:#888;margin-top:4px}}.empty{{color:#777}}.exceptions{{border-color:#473333}}.consequence{{margin-top:12px;min-height:0}}.consequence-head{{display:flex;justify-content:space-between;gap:20px;align-items:flex-start}}.consequence-head h3{{margin-bottom:4px}}.graph-counts{{display:flex;flex-wrap:wrap;gap:6px;justify-content:flex-end}}.graph-count{{border:1px solid #343434;border-radius:999px;padding:5px 8px;font-size:.72rem;color:#999}}.graph-count b{{color:#ddd}}.graph-edges{{margin-top:12px;border-top:1px solid #2b2b2b}}.graph-edge{{display:grid;grid-template-columns:minmax(0,1fr) 150px minmax(0,1fr);gap:12px;align-items:center}}.graph-node{{background:#141414;border:1px solid #292929;border-radius:7px;padding:8px 10px;overflow-wrap:anywhere}}.graph-node i{{display:block;color:#777;font-size:.64rem;text-transform:uppercase;letter-spacing:.08em;font-style:normal;margin-bottom:3px}}.graph-relation{{text-align:center;color:#8e9eae;font-size:.72rem;text-transform:uppercase;letter-spacing:.07em}}@media(max-width:950px){{.metrics{{grid-template-columns:repeat(3,1fr)}}.grid{{grid-template-columns:1fr 1fr}}.evidence-grid,.activity,.decision-lower{{grid-template-columns:1fr}}.decision-context{{grid-template-columns:1fr 1fr}}}}@media(max-width:650px){{.graph-edge{{grid-template-columns:1fr;gap:5px}}.graph-relation{{text-align:left;padding-left:10px}}.consequence-head{{display:block}}.graph-counts{{justify-content:flex-start;margin-top:12px}}}}@media(max-width:560px){{main{{padding:24px 16px 56px}}.top{{display:block}}.system{{text-align:left;margin-top:16px}}.metrics{{grid-template-columns:1fr 1fr}}.current,.grid,.decision-context{{grid-template-columns:1fr}}}}
</style></head><body><main><div class='top'><div><p class='eyebrow'>Human supervision</p><h1>Lattice</h1><p class='lede'>What the agency is doing, what changed, how long attention has been waiting, and where human authority is required. This surface is read-only; authority remains in the guarded state engine.</p></div><div class='system'><span class='backend'>{html.escape(backend)} state</span><div class='revision'>revision {model['revision']} · event {model['event_sequence']}</div></div></div><div class='metrics'>{metrics}</div><section class='principal'><header><div><p class='eyebrow'>Human decision boundary</p><h2>Principal inbox</h2></div><div class='count'>{inbox['count']} open · {inbox['blocking_count']} blocking</div></header>{decision_cards}</section><section class='activity'><article><h3>Recent accepted changes <b>{len(changes)}</b></h3><ul>{change_rows}</ul></article><article><h3>Operational telemetry</h3><div class='telemetry'>{telemetry_metrics}</div></article></section>{body}</main></body></html>"""


class ControlHandler(BaseHTTPRequestHandler):
    server_version = "LatticeControl/0.0.7"

    def _model(self) -> dict:
        query = parse_qs(urlparse(self.path).query)
        project_id = query.get("project", [None])[0]
        with open_state_store(ROOT) as store:
            return supervision_model(store, project_id, 5)

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
    parser=argparse.ArgumentParser(description="Serve Lattice's local read-only control surface over the configured state backend."); parser.add_argument("--host", default="127.0.0.1"); parser.add_argument("--port", type=int, default=8765); args=parser.parse_args()
    server=ThreadingHTTPServer((args.host,args.port),ControlHandler); print(f"Lattice control surface: http://{args.host}:{args.port}")
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
