#!/usr/bin/env python3
"""Local human control surface for Lattice."""

from __future__ import annotations

import argparse
import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse

from concurrency import claim_for_host_atomic
from lifecycle import fulfill_commitment_action, resolve_exception_action
from state_engine import LatticeError
from store_factory import open_state_store
from supervision import principal_inbox
from supervision_model import supervision_model

ROOT = Path(__file__).resolve().parents[1]


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


def _safe(value: object) -> str:
    return html.escape(str(value))


def _headline(model: dict) -> tuple[str, str]:
    portfolio = model.get("portfolio") or {}
    inbox = model.get("principal_inbox") or {}
    blocking = int(inbox.get("blocking_count", 0))
    decisions = int(inbox.get("count", 0))
    in_flight = int(portfolio.get("in_flight", 0))
    verification = int(portfolio.get("pending_verification", 0))
    ready = int(portfolio.get("ready_actions", 0))
    if blocking:
        return (
            f"{blocking} decision{'s' if blocking != 1 else ''} need your attention.",
            "Progress is blocked at an authority boundary. Decide here; Lattice will keep the decision in durable project history.",
        )
    if decisions:
        return (
            f"{decisions} decision{'s' if decisions != 1 else ''} are yours, but work can continue.",
            "Everything below the decision boundary remains delegated unless the state changes.",
        )
    if in_flight or verification:
        return (
            "Work is progressing without your attention.",
            f"{in_flight} in flight · {verification} awaiting verification · {ready} ready next.",
        )
    if ready:
        return ("The frontier is ready to move.", f"{ready} action{'s' if ready != 1 else ''} can be claimed now.")
    return ("No human action is required.", "Lattice has no ready or in-flight work in the current view.")


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


def _list(items: list[dict], primary, secondary, *, empty: str = "None") -> str:
    if not items:
        return f"<p class='empty'>{_safe(empty)}</p>"
    return "<ul class='rows'>" + "".join(
        f"<li><strong>{_safe(primary(item))}</strong><span>{_safe(secondary(item))}</span></li>"
        for item in items
    ) + "</ul>"


def _decision_cards(items: list[dict]) -> str:
    if not items:
        return "<div class='quiet'><strong>Nothing needs your decision.</strong><span>Authority remains delegated.</span></div>"
    cards: list[str] = []
    for item in items:
        affected = item.get("affected_state") or {}
        objective = affected.get("active_objective") or {}
        milestone = affected.get("active_milestone") or {}
        target = affected.get("target") or {}
        target_state = target.get("state") or {}
        target_summary = target_state.get("title") or target_state.get("key") or target.get("id") or "No specific target"
        evidence = item.get("evidence") or []
        evidence_html = _list(
            evidence,
            lambda x: x.get("summary") or x.get("entity_id"),
            lambda x: " · ".join(part for part in [x.get("role"), x.get("source_ref")] if part),
            empty="No durable evidence is attached to this decision target.",
        )
        choices = {choice.get("choice"): choice for choice in item.get("supported_choices", [])}
        action_choice = "resolve" if item["kind"] == "exception" else "fulfill"
        action = choices.get(action_choice) or {}
        note_label = "Record the decision" if item["kind"] == "exception" else "Record fulfillment"
        button_label = "Resolve exception" if item["kind"] == "exception" else "Confirm fulfilled"
        cards.append(f"""
<article class='decision'>
  <div class='decision-top'>
    <div><span class='kicker'>{_safe(item['project_id'])} · {_safe(item['kind'])}</span><h2>{_safe(item['title'])}</h2></div>
    <span class='pill attention'>{'BLOCKING' if item.get('blocking') else 'DECISION'}</span>
  </div>
  <p class='decision-question'>{_safe(item['decision_required'])}</p>
  <p class='detail'>{_safe(item.get('detail') or '')}</p>
  <div class='impact'>
    <div><span>What this controls</span><strong>{_safe(target_summary)}</strong></div>
    <div><span>Current milestone</span><strong>{_safe(milestone.get('title') or 'None active')}</strong></div>
    <div><span>If you act</span><strong>{_safe(action.get('consequence') or 'The guarded state transition will be recorded.')}</strong></div>
  </div>
  <form method='post' action='/action' class='decision-form'>
    <input type='hidden' name='action_key' value='{_safe(item['action_key'])}'>
    <input type='hidden' name='choice' value='{_safe(action_choice)}'>
    <label>{_safe(note_label)}<textarea name='note' required rows='2' placeholder='State the decision and any constraint agents should preserve.'></textarea></label>
    <button type='submit'>{_safe(button_label)}</button>
  </form>
  <details><summary>Why this is yours · evidence · context</summary>
    <div class='detail-grid'>
      <div><h3>Authority boundary</h3><p>{_safe(item['authority_reason'])}</p></div>
      <div><h3>Evidence</h3>{evidence_html}</div>
      <div><h3>Objective</h3><p>{_safe(objective.get('title') or 'None active')}</p><h3>Semantic revision</h3><p>r{_safe(affected.get('semantic_revision', '—'))}</p></div>
    </div>
  </details>
</article>""")
    return "".join(cards)


def _project_card(item: dict) -> str:
    project = item["project"]
    objective = item.get("objective") or {}
    milestone = item.get("milestone") or {}
    frontier = item.get("frontier") or []
    leases = item.get("active_leases") or []
    verification = item.get("pending_verification") or []
    exceptions = item.get("open_exceptions") or []
    temporal = item.get("temporal_health") or {}
    blocked = temporal.get("blocked_conditions") or []
    readiness = item.get("readiness") or {}
    evidence = item.get("evidence_chain") or []
    truths = item.get("frontier_truths") or []
    graph = item.get("consequence_graph") or {}
    now_items = []
    for lease in leases:
        now_items.append({"title": lease["leased_by"], "meta": f"{lease['role']} · {_duration(lease.get('age_seconds'))} active · {_duration(max(0, lease.get('remaining_seconds', 0)))} lease left"})
    for pending in verification:
        now_items.append({"title": pending["title"], "meta": f"verification · waiting for {pending['verifier_role']} · {_duration(pending.get('waiting_seconds'))}"})
    attention = []
    for exception in exceptions:
        attention.append({"title": exception["title"], "meta": f"{exception['severity']} · {exception['owner_role']} · open {_duration(exception.get('open_seconds'))}"})
    for condition in blocked:
        attention.append({"title": condition["title"], "meta": f"blocked · {condition['owner_role']} · attempts {condition['attempt_count']}/{condition['attempt_budget']}"})
    status = "needs attention" if attention else ("working" if now_items else ("ready" if frontier else "quiet"))
    details = _list(
        evidence,
        lambda x: x.get("condition_title") or x.get("summary") or x.get("entity_id"),
        lambda x: " · ".join(part for part in [x.get("entity_type"), x.get("role"), x.get("review_verdict"), x.get("source_ref")] if part),
        empty="No evidence recorded yet.",
    )
    graph_counts = " · ".join(f"{count} {kind}" for kind, count in (graph.get("counts") or {}).items() if count) or "No consequence links"
    return f"""
<article class='project-card'>
  <header><div><span class='kicker'>{_safe(project['id'])}</span><h2>{_safe(project['name'])}</h2></div><span class='pill'>{_safe(status.upper())}</span></header>
  <div class='goal'><span>Working toward</span><strong>{_safe(objective.get('title') or 'No active objective')}</strong><small>{_safe(milestone.get('title') or 'No active milestone')}</small></div>
  <div class='project-columns'>
    <section><h3>Now <b>{len(now_items)}</b></h3>{_list(now_items, lambda x:x['title'], lambda x:x['meta'], empty='Nothing is currently executing or waiting for verification.')}</section>
    <section><h3>Next <b>{len(frontier)}</b></h3>{_list(frontier, lambda x:x['title'], lambda x:f"{x['role']} · {x['kind']}", empty='No ready action.')}</section>
    <section class='attention-col'><h3>Needs attention <b>{len(attention)}</b></h3>{_list(attention, lambda x:x['title'], lambda x:x['meta'], empty='No exception or blocked condition.')}</section>
  </div>
  <div class='project-foot'><span>Milestone <b>{'ready' if readiness.get('ready') else 'not ready'}</b></span><span>Oldest attention <b>{_duration(temporal.get('oldest_attention_seconds'))}</b></span><span>semantic r{_safe(item.get('semantic_revision', '—'))}</span></div>
  <details><summary>Inspect evidence and consequence state</summary>
    <div class='inspect-grid'><section><h3>Evidence <b>{len(evidence)}</b></h3>{details}</section><section><h3>Frontier truths <b>{len(truths)}</b></h3>{_list(truths, lambda x:x['statement'], lambda x:f"{x['epistemic_status']} · v{x['version']}")}</section><section><h3>Consequence graph</h3><p class='detail'>{_safe(graph_counts)}. Full graph remains available through <code>/api/state</code>.</p></section></div>
  </details>
</article>"""


def apply_principal_action(store, action_key: str, choice: str, note: str) -> dict:
    """Execute only a currently advertised Principal choice through the guarded lifecycle."""
    note = note.strip()
    if not note:
        raise LatticeError("A recorded decision or fulfillment summary is required")
    inbox = principal_inbox(store)
    item = next((candidate for candidate in inbox["items"] if candidate["action_key"] == action_key), None)
    if item is None:
        raise LatticeError("This Principal action is no longer current")
    supported = {candidate["choice"] for candidate in item.get("supported_choices", [])}
    if choice not in supported or choice == "leave_open":
        raise LatticeError("Unsupported mutating choice for this Principal action")
    expected = "resolve" if item["kind"] == "exception" else "fulfill"
    if choice != expected:
        raise LatticeError("Choice does not match the durable action type")
    claimed = claim_for_host_atomic(
        store,
        project_id=item["project_id"],
        role="principal",
        actor="principal-ui",
        host="human-control-surface",
        action_key=action_key,
    )
    if item["kind"] == "exception":
        result = resolve_exception_action(store, claimed["lease_id"], "principal", note)
    elif item["kind"] == "commitment":
        result = fulfill_commitment_action(store, claimed["lease_id"], "principal", note)
    else:
        raise LatticeError("Unsupported Principal action type")
    return {"kind": item["kind"], "action_key": action_key, "result": result}


def render_html(model: dict, flash: str | None = None, flash_error: bool = False) -> str:
    inbox = model.get("principal_inbox") or {"count": 0, "blocking_count": 0, "items": []}
    portfolio = model.get("portfolio") or {}
    telemetry = model.get("operational_telemetry") or {}
    headline, lede = _headline(model)
    projects = "".join(_project_card(item) for item in model.get("projects", [])) or "<p class='empty'>No projects are registered.</p>"
    changes = model.get("recent_accepted_changes") or []
    change_html = _list(changes[:8], _change_label, lambda x:f"{x['project_id']} · {x['role']} · r{x['revision']} · {x['created_at']}", empty="No accepted changes recorded yet.")
    flash_html = f"<div class='flash {'error' if flash_error else ''}'>{_safe(flash)}</div>" if flash else ""
    system_bits = [
        f"backend {_safe(model.get('state_backend', 'sqlite'))}",
        f"{telemetry.get('retries', 0)} retries",
        f"{telemetry.get('recoveries', 0)} recoveries",
        f"{telemetry.get('worker_failures', 0)} worker failures",
        f"median action {_duration(telemetry.get('median_action_duration_seconds'))}",
    ]
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Lattice Control</title><style>
:root{{color-scheme:dark;font-family:Inter,ui-sans-serif,system-ui,sans-serif;background:#0d0f11;color:#f3f4f5}}*{{box-sizing:border-box}}body{{margin:0;background:#0d0f11;color:#f3f4f5}}main{{max-width:1180px;margin:auto;padding:32px 24px 72px}}h1,h2,h3,p{{margin-top:0}}h1{{font-size:clamp(2rem,5vw,4.6rem);line-height:.96;letter-spacing:-.055em;margin-bottom:14px;max-width:900px}}h2{{letter-spacing:-.025em}}h3{{font-size:.78rem;text-transform:uppercase;letter-spacing:.08em;color:#9aa1a8}}.hero{{padding:24px 0 30px;border-bottom:1px solid #272b2f}}.hero-top{{display:flex;justify-content:space-between;gap:24px;align-items:flex-start}}.brand{{font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:#747c84}}.lede,.detail{{color:#aab0b6;line-height:1.5;max-width:760px}}.summary-strip{{display:flex;gap:20px;flex-wrap:wrap;margin-top:20px;color:#aab0b6;font-size:.86rem}}.summary-strip b{{color:#f3f4f5}}.flash{{margin:18px 0 0;padding:12px 14px;border:1px solid #315844;background:#102119;border-radius:8px;color:#bfe3ce}}.flash.error{{border-color:#713c3c;background:#241313;color:#f0bbbb}}.section-head{{display:flex;justify-content:space-between;gap:20px;align-items:end;margin:34px 0 12px}}.section-head h2{{margin:0;font-size:1.05rem}}.section-head p{{margin:0;color:#747c84;font-size:.82rem}}.decision,.project-card,.quiet,.activity{{border:1px solid #292e33;background:#131619;border-radius:12px;padding:18px;margin-bottom:12px}}.decision{{border-color:#66502e;background:#18150f}}.decision-top,.project-card>header{{display:flex;justify-content:space-between;gap:18px;align-items:flex-start}}.decision h2,.project-card h2{{font-size:1.25rem;margin:3px 0 0}}.decision-question{{font-size:1.05rem;line-height:1.4;margin:18px 0 8px;max-width:800px}}.kicker{{font-size:.68rem;text-transform:uppercase;letter-spacing:.1em;color:#7f878f}}.pill{{border:1px solid #3b4249;border-radius:999px;padding:5px 8px;font-size:.64rem;letter-spacing:.08em;color:#abb2b9;white-space:nowrap}}.pill.attention{{border-color:#7a5a2d;color:#e1bd7e}}.impact{{display:grid;grid-template-columns:1fr 1fr 2fr;gap:8px;margin:18px 0}}.impact>div,.goal{{background:#101214;border-radius:8px;padding:12px}}.impact span,.goal span{{display:block;color:#737b83;text-transform:uppercase;letter-spacing:.08em;font-size:.65rem;margin-bottom:5px}}.impact strong,.goal strong{{font-size:.87rem;line-height:1.4}}.decision-form{{display:grid;grid-template-columns:1fr auto;gap:10px;align-items:end;padding-top:4px}}label{{font-size:.72rem;color:#9aa1a8;text-transform:uppercase;letter-spacing:.06em}}textarea{{display:block;width:100%;margin-top:7px;resize:vertical;border:1px solid #3b4249;background:#0d0f11;color:#f3f4f5;border-radius:8px;padding:10px;font:inherit;text-transform:none;letter-spacing:0}}button{{border:0;border-radius:8px;background:#e8e3d8;color:#111;padding:11px 16px;font-weight:700;cursor:pointer;min-height:42px}}button:hover{{background:#fff}}details{{border-top:1px solid #292e33;margin-top:16px;padding-top:12px}}summary{{cursor:pointer;color:#90979e;font-size:.78rem}}.detail-grid,.inspect-grid{{display:grid;grid-template-columns:1fr 1.4fr .7fr;gap:16px;margin-top:14px}}.detail-grid p{{color:#aab0b6;line-height:1.45;font-size:.85rem}}.quiet{{display:flex;justify-content:space-between;gap:12px;color:#98a0a8}}.quiet span{{color:#697078}}.goal{{margin:14px 0}}.goal small{{display:block;color:#8d949a;margin-top:4px}}.project-columns{{display:grid;grid-template-columns:repeat(3,1fr);gap:9px}}.project-columns>section{{border:1px solid #252a2e;border-radius:9px;padding:12px;min-width:0}}.project-columns h3{{display:flex;justify-content:space-between;margin-bottom:10px}}.project-columns h3 b{{color:#d2d6da}}.attention-col:not(:has(.empty)){{border-color:#5a4930}}.rows{{list-style:none;margin:0;padding:0}}.rows li{{padding:9px 0;border-top:1px solid #24292d}}.rows li:first-child{{border-top:0;padding-top:0}}.rows strong,.rows span{{display:block}}.rows strong{{font-size:.86rem;line-height:1.35}}.rows span{{color:#737b83;font-size:.72rem;margin-top:3px;line-height:1.35}}.empty{{color:#626970;font-size:.8rem;line-height:1.4;margin:0}}.project-foot{{display:flex;gap:18px;flex-wrap:wrap;color:#747c84;font-size:.72rem;margin-top:12px}}.project-foot b{{color:#bcc2c7}}.activity-grid{{display:grid;grid-template-columns:2fr 1fr;gap:12px}}.system-list{{color:#858d94;font-size:.8rem;line-height:1.8;margin:0;padding-left:18px}}code{{font-family:ui-monospace,monospace;color:#8d959c}}@media(max-width:800px){{main{{padding:22px 14px 56px}}.hero-top,.decision-top,.project-card>header,.section-head{{align-items:flex-start}}.impact,.project-columns,.detail-grid,.inspect-grid,.activity-grid{{grid-template-columns:1fr}}.decision-form{{grid-template-columns:1fr}}button{{width:100%}}.quiet{{display:block}}.quiet span{{display:block;margin-top:4px}}}}@media(max-width:520px){{h1{{font-size:2.55rem}}.hero-top{{display:block}}.hero-top .brand{{margin-bottom:14px}}.decision,.project-card,.quiet,.activity{{padding:14px}}.impact{{margin:14px 0}}.section-head{{margin-top:28px}}}}
</style></head><body><main>
<section class='hero'><div class='hero-top'><div class='brand'>Lattice / Human control</div><code>0.1.1 · {_safe(model.get('state_backend','sqlite'))}</code></div><h1>{_safe(headline)}</h1><p class='lede'>{_safe(lede)}</p><div class='summary-strip'><span><b>{portfolio.get('active_projects',0)}</b> active projects</span><span><b>{portfolio.get('in_flight',0)}</b> in flight</span><span><b>{portfolio.get('pending_verification',0)}</b> verification</span><span><b>{portfolio.get('ready_actions',0)}</b> ready next</span><span><b>{portfolio.get('open_exceptions',0)}</b> exceptions</span></div>{flash_html}</section>
<div class='section-head'><h2>Your decisions</h2><p>{inbox.get('blocking_count',0)} blocking · {inbox.get('count',0)} total</p></div>{_decision_cards(inbox.get('items',[]))}
<div class='section-head'><h2>Projects</h2><p>Now → next → attention</p></div>{projects}
<div class='section-head'><h2>What changed</h2><p>Accepted durable state only</p></div><div class='activity-grid'><section class='activity'>{change_html}</section><section class='activity'><h3>System health</h3><ul class='system-list'>{''.join(f'<li>{bit}</li>' for bit in system_bits)}</ul></section></div>
</main></body></html>"""


class ControlHandler(BaseHTTPRequestHandler):
    server_version = "LatticeControl/0.1.1"

    def _model(self) -> dict:
        query = parse_qs(urlparse(self.path).query)
        project_id = query.get("project", [None])[0]
        with open_state_store(ROOT) as store:
            return supervision_model(store, project_id, 5)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        try:
            if parsed.path == "/api/state":
                payload = json.dumps(self._model(), indent=2, sort_keys=True).encode()
                status, content_type = 200, "application/json; charset=utf-8"
            elif parsed.path in {"/", "/index.html"}:
                payload = render_html(self._model(), query.get("message", [None])[0], query.get("error", ["0"])[0] == "1").encode()
                status, content_type = 200, "text/html; charset=utf-8"
            elif parsed.path == "/health":
                payload, status, content_type = b'{"ok":true}\n', 200, "application/json; charset=utf-8"
            else:
                payload, status, content_type = b"Not found\n", 404, "text/plain; charset=utf-8"
        except LatticeError as error:
            payload = json.dumps({"error": str(error)}).encode()
            status, content_type = 400, "application/json; charset=utf-8"
        self._send(status, content_type, payload)

    def do_POST(self) -> None:  # noqa: N802
        if urlparse(self.path).path != "/action":
            self._send(404, "text/plain; charset=utf-8", b"Not found\n")
            return
        length = int(self.headers.get("Content-Length", "0"))
        form = parse_qs(self.rfile.read(length).decode("utf-8"), keep_blank_values=True)
        try:
            action_key = form.get("action_key", [""])[0]
            choice = form.get("choice", [""])[0]
            note = form.get("note", [""])[0]
            with open_state_store(ROOT) as store:
                result = apply_principal_action(store, action_key, choice, note)
            message = "Decision recorded: " + result["kind"]
            location = "/?" + urlencode({"message": message})
        except (LatticeError, KeyError, ValueError) as error:
            location = "/?" + urlencode({"message": str(error), "error": "1"})
        self.send_response(303)
        self.send_header("Location", location)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def _send(self, status: int, content_type: str, payload: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve Lattice's local human control surface over the configured state backend.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), ControlHandler)
    print(f"Lattice control surface: http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
