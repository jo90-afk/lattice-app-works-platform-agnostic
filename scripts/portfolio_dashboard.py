#!/usr/bin/env python3
"""Human portfolio and project-detail renderers for Lattice."""

from __future__ import annotations

import html
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
RELEASE = (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def _safe(value: object) -> str:
    return html.escape(str(value))


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
    return f"{hours}h {minutes % 60}m"


def _status_tone(status: str) -> str:
    return {
        "working": "green",
        "verification": "blue",
        "ready": "green",
        "attention": "amber",
        "blocked": "red",
        "quiet": "neutral",
    }.get(status, "neutral")


def _agent_rows(project: dict) -> list[dict]:
    rows: dict[str, dict] = {}

    def put(role: str, status: str, task: str, detail: str = "") -> None:
        priority = {"blocked": 5, "working": 4, "verification": 3, "ready": 2, "quiet": 1}
        current = rows.get(role)
        candidate = {"role": role, "status": status, "task": task, "detail": detail}
        if current is None or priority.get(status, 0) > priority.get(current["status"], 0):
            rows[role] = candidate

    for lease in project.get("active_leases") or []:
        put(
            str(lease.get("role", "agent")),
            "working",
            str(lease.get("leased_by") or "Working"),
            f"active {_duration(lease.get('age_seconds'))} · {_duration(lease.get('remaining_seconds'))} lease left",
        )
    for pending in project.get("pending_verification") or []:
        put(
            str(pending.get("verifier_role") or "quality"),
            "verification",
            str(pending.get("title") or "Independent verification"),
            f"waiting {_duration(pending.get('waiting_seconds'))}",
        )
    for action in project.get("frontier") or []:
        role = str(action.get("role") or "agent")
        if role == "principal":
            continue
        put(role, "ready", str(action.get("title") or action.get("kind") or "Ready work"), str(action.get("kind") or "ready"))
    temporal = project.get("temporal_health") or {}
    for condition in temporal.get("blocked_conditions") or []:
        put(
            str(condition.get("owner_role") or "director"),
            "blocked",
            str(condition.get("title") or "Blocked condition"),
            f"attempts {condition.get('attempt_count', 0)}/{condition.get('attempt_budget', '—')}",
        )
    if (project.get("readiness") or {}).get("ready"):
        put("assurance", "ready", "Milestone ready for acceptance", "readiness satisfied")
    return sorted(rows.values(), key=lambda row: (row["status"] not in {"working", "verification", "blocked"}, row["role"]))


def _progress(project: dict) -> tuple[int, str]:
    readiness = project.get("readiness") or {}
    conditions = readiness.get("conditions") or []
    if conditions:
        satisfied = sum(1 for condition in conditions if condition.get("status") in {"satisfied", "waived"})
        pct = round((satisfied / len(conditions)) * 100)
        return pct, f"{satisfied}/{len(conditions)} readiness conditions satisfied"
    if readiness.get("ready"):
        return 100, "Milestone ready"
    if project.get("milestone"):
        return 18, "Milestone active"
    return 0, "No active milestone"


def _project_state(project: dict) -> tuple[str, str]:
    agents = _agent_rows(project)
    inbox = project.get("principal_decisions") or []
    blocked = (project.get("temporal_health") or {}).get("blocked_conditions") or []
    exceptions = project.get("open_exceptions") or []
    if inbox:
        return "attention", "Human decision"
    if blocked:
        return "blocked", "Blocked"
    if exceptions:
        return "attention", "Exception managed"
    if any(agent["status"] == "working" for agent in agents):
        return "working", "Active"
    if any(agent["status"] == "verification" for agent in agents):
        return "verification", "Verification"
    if project.get("frontier"):
        return "ready", "Ready"
    return "quiet", "Stable"


def _agent_table(project: dict) -> str:
    agents = _agent_rows(project)
    if not agents:
        return "<div class='empty-row'>No agent currently holds or awaits project work.</div>"
    rows = []
    for agent in agents:
        tone = _status_tone(agent["status"])
        initials = "".join(part[:1].upper() for part in agent["role"].replace("_", " ").split()[:2]) or "A"
        rows.append(
            f"<div class='agent-row'><div class='avatar {tone}'>{_safe(initials)}</div>"
            f"<div class='agent-name'><strong>{_safe(agent['role'].title())}</strong><span>{_safe(agent['task'])}</span></div>"
            f"<div class='agent-state {tone}'><i></i>{_safe(agent['status'].replace('_',' ').title())}</div>"
            f"<div class='agent-detail'>{_safe(agent['detail'])}</div></div>"
        )
    return "".join(rows)


def _decision_strip(inbox: dict) -> str:
    items = inbox.get("items") or []
    if not items:
        return ""
    cards = []
    for item in items:
        affected = item.get("affected_state") or {}
        target = affected.get("target") or {}
        target_state = target.get("state") or {}
        milestone = (
            target_state if target.get("type") == "milestone" and target_state
            else affected.get("active_milestone")
            or affected.get("latest_accepted_milestone")
            or {}
        )
        milestone_status = str(milestone.get("status") or "").replace("_", " ").title()
        cards.append(
            "<article class='decision-card'>"
            f"<div><span class='eyebrow'>Principal exception · {_safe(item['project_id'])}</span>"
            f"<h2>{_safe(item['title'])}</h2><p>{_safe(item.get('detail') or item.get('decision_required') or '')}</p>"
            f"<span class='decision-context'>{_safe(milestone.get('title') or 'Project-level decision')}{' · ' + _safe(milestone_status) if milestone_status else ''}</span></div>"
            f"<a class='button secondary' href='/project?project={quote(str(item['project_id']))}'>Review exception</a>"
            "</article>"
        )
    return "<section class='exceptions'><div class='section-title'><h2>Needs your decision</h2><span>Only consequence-boundary exceptions appear here</span></div>" + "".join(cards) + "</section>"


def _project_card(project: dict) -> str:
    meta = project["project"]
    objective = project.get("objective") or {}
    milestone = project.get("current_milestone") or project.get("milestone") or {}
    if milestone and milestone.get("status") == "accepted" and not project.get("milestone"):
        pct, progress_label = 100, "Latest milestone accepted"
    else:
        pct, progress_label = _progress(project)
    state, state_label = _project_state(project)
    agents = _agent_rows(project)
    exceptions = [e for e in (project.get("open_exceptions") or []) if not e.get("principal_only")]
    return f"""
<article class='project-card'>
  <div class='project-head'>
    <div><span class='eyebrow'>{_safe(meta['id'])}</span><h2>{_safe(meta['name'])}</h2></div>
    <span class='project-status {_status_tone(state)}'><i></i>{_safe(state_label)}</span>
  </div>
  <p class='objective'>{_safe(objective.get('title') or 'No active objective')}</p>
  <div class='progress-line'><div class='progress-copy'><strong>{_safe(milestone.get('title') or 'No active milestone')}</strong><span>{pct}%</span></div><div class='bar'><b style='width:{pct}%'></b></div><small>{_safe(progress_label)}</small></div>
  <div class='agent-header'><span>Agents</span><span>{len(agents)} active / assigned</span></div>
  <div class='agents'>{_agent_table(project)}</div>
  <div class='project-foot'>
    <span>{len(exceptions)} managed exception{'s' if len(exceptions) != 1 else ''}</span>
    <span>{len(project.get('frontier') or [])} ready action{'s' if len(project.get('frontier') or []) != 1 else ''}</span>
    <a href='/project?project={quote(str(meta['id']))}'>Project detail →</a>
  </div>
</article>"""


def _styles() -> str:
    return """
:root{font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:#26312b;background:#f5f1e8;--ink:#26312b;--muted:#788077;--line:#e5dfd3;--card:#fffdfa;--green:#789273;--green-soft:#e9f0e5;--amber:#bd955a;--amber-soft:#f8eedc;--red:#b76d62;--red-soft:#f8e9e6;--blue:#7893a5;--blue-soft:#e9eff3}*{box-sizing:border-box}body{margin:0;background:#f5f1e8;color:var(--ink)}a{color:inherit;text-decoration:none}header.top{height:60px;padding:0 28px;background:#fbfaf6;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between}.brand{font-family:Georgia,serif;font-weight:700;font-size:20px;letter-spacing:.14em}.brand-mark{display:inline-grid;place-items:center;width:27px;height:27px;border:2px solid #83927d;border-radius:50%;margin-right:9px;color:#83927d;font-size:12px}.nav{display:flex;gap:26px;align-items:center;color:#6f776f;font-size:13px}.nav strong{color:#334037}.nav b{background:#eff1ec;border-radius:999px;padding:3px 7px;font-size:11px;color:#5f6e5b}.nav .agent-nav{color:#47714a}.principal{width:28px;height:28px;border-radius:50%;background:#d9e4d4;color:#5e7659;display:grid;place-items:center;font-weight:700;font-size:12px}main{max-width:1160px;margin:0 auto;padding:40px 24px 72px}.portfolio-title{margin-bottom:22px}.portfolio-title h1{font-family:Georgia,serif;font-size:31px;margin:0 0 5px;font-weight:500}.portfolio-title p{margin:0;color:#8a8e87;font-family:Georgia,serif;font-size:14px;font-style:italic}.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:24px 0 30px}.metric{background:var(--card);border:1px solid var(--line);border-radius:9px;padding:16px 18px;box-shadow:0 2px 10px rgba(65,55,40,.035)}.metric span{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#9b9c96}.metric strong{display:block;font-family:Georgia,serif;font-size:27px;font-weight:500;margin-top:5px}.metric small{display:block;margin-top:4px;color:#8f938b;font-size:11px}.section-title{display:flex;align-items:end;justify-content:space-between;margin:26px 0 11px}.section-title h2{font-family:Georgia,serif;font-size:18px;font-weight:500;margin:0}.section-title span{font-size:11px;color:#9a9e96}.project-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.project-card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:18px 19px;box-shadow:0 3px 14px rgba(72,62,45,.045)}.project-head{display:flex;justify-content:space-between;gap:16px}.eyebrow{font-size:10px;text-transform:uppercase;letter-spacing:.11em;color:#9a9d96}.project-head h2{font-family:Georgia,serif;font-size:22px;margin:4px 0 0;font-weight:500}.project-status{height:25px;padding:0 9px;border-radius:999px;display:flex;align-items:center;gap:6px;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.06em}.project-status i,.agent-state i{width:6px;height:6px;border-radius:50%;display:inline-block;background:currentColor}.green{color:#587653}.project-status.green{background:var(--green-soft)}.amber{color:#916d38}.project-status.amber{background:var(--amber-soft)}.red{color:#9c5d54}.project-status.red{background:var(--red-soft)}.blue{color:#58778a}.project-status.blue{background:var(--blue-soft)}.neutral{color:#7c817a}.project-status.neutral{background:#efefeb}.objective{margin:12px 0 15px;color:#687067;font-size:13px;line-height:1.45}.progress-line{border-top:1px solid #eee9df;border-bottom:1px solid #eee9df;padding:12px 0}.progress-copy{display:flex;justify-content:space-between;gap:12px;font-size:11px}.progress-copy strong{font-weight:600}.progress-copy span{color:#72866d}.bar{height:5px;background:#ecebe5;border-radius:99px;margin:8px 0 5px;overflow:hidden}.bar b{display:block;height:100%;background:#8da486;border-radius:99px}.progress-line small{font-size:10px;color:#979b94}.agent-header{display:flex;justify-content:space-between;margin:14px 0 5px;font-size:10px;text-transform:uppercase;letter-spacing:.08em;color:#9a9d96}.agents{border-top:1px solid #eee9df}.agent-row{display:grid;grid-template-columns:29px minmax(0,1.4fr) 80px minmax(0,1fr);gap:8px;align-items:center;border-bottom:1px solid #f0ece4;padding:9px 0}.avatar{width:25px;height:25px;border-radius:50%;display:grid;place-items:center;font-size:9px;font-weight:800;background:#eef0eb}.avatar.green{background:var(--green-soft)}.avatar.amber{background:var(--amber-soft)}.avatar.red{background:var(--red-soft)}.avatar.blue{background:var(--blue-soft)}.agent-name strong{font-size:11px;display:block}.agent-name span{font-size:10px;color:#858b83;display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:2px}.agent-state{font-size:9px;display:flex;align-items:center;gap:5px;text-transform:uppercase;letter-spacing:.04em}.agent-detail{font-size:9px;color:#9a9e96;text-align:right}.empty-row{padding:12px 0;color:#9a9e96;font-size:11px}.project-foot{display:flex;gap:14px;align-items:center;margin-top:12px;color:#8f948c;font-size:10px}.project-foot a{margin-left:auto;color:#62785e;font-weight:700}.exceptions{margin-bottom:26px}.decision-card{background:#fffaf1;border:1px solid #ead9b8;border-radius:10px;padding:16px 18px;display:flex;justify-content:space-between;gap:20px;align-items:center}.decision-card h2{font-family:Georgia,serif;font-size:17px;margin:4px 0 5px}.decision-card p{margin:0;color:#776e61;font-size:12px}.decision-context{display:block;font-size:10px;color:#9f927e;margin-top:6px}.button{border-radius:7px;padding:9px 12px;font-size:11px;font-weight:700;white-space:nowrap}.button.secondary{border:1px solid #d9c7a5;background:white}.detail-shell{max-width:980px}.back{font-size:12px;color:#71806d}.detail-shell h1{font-family:Georgia,serif;font-size:30px;font-weight:500;margin:18px 0 8px}.detail-card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:18px;margin-top:15px}.detail-card h2{font-family:Georgia,serif;font-size:18px;font-weight:500;margin:0 0 12px}.detail-list{font-size:12px;line-height:1.7;color:#666f66}.detail-list strong{color:#2f3932}.flash{margin:0 0 18px;padding:10px 12px;border:1px solid #bdd0b7;background:#eef5eb;border-radius:7px;color:#54714f;font-size:12px}.flash.error{border-color:#e0bbb4;background:#fbefed;color:#945b52}@media(max-width:850px){.project-grid{grid-template-columns:1fr}.metrics{grid-template-columns:repeat(2,1fr)}.nav span:nth-child(-n+2){display:none}}@media(max-width:580px){header.top{padding:0 14px}.nav{gap:12px}.nav .agent-nav{display:none}main{padding:28px 14px 50px}.metrics{grid-template-columns:1fr 1fr}.metric{padding:13px}.agent-row{grid-template-columns:27px 1fr 72px}.agent-detail{display:none}.project-card{padding:15px}.decision-card{display:block}.decision-card .button{display:inline-block;margin-top:12px}}
"""


def render_portfolio_html(model: dict, flash: str | None = None, flash_error: bool = False) -> str:
    portfolio = model.get("portfolio") or {}
    inbox = model.get("principal_inbox") or {"count": 0, "items": []}
    projects = [item for item in (model.get("projects") or []) if (item.get("project") or {}).get("status") == "active"]
    principal_by_project: dict[str, list[dict]] = {}
    for decision in inbox.get("items") or []:
        principal_by_project.setdefault(str(decision.get("project_id")), []).append(decision)
    cards = []
    all_agents = 0
    for raw in projects:
        project = dict(raw)
        project["principal_decisions"] = principal_by_project.get(str(project["project"]["id"]), [])
        all_agents += len(_agent_rows(project))
        cards.append(_project_card(project))
    managed_exceptions = sum(len([e for e in (p.get("open_exceptions") or []) if not e.get("principal_only")]) for p in projects)
    changes = model.get("recent_accepted_changes") or []
    flash_html = f"<div class='flash {'error' if flash_error else ''}'>{_safe(flash)}</div>" if flash else ""
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Lattice · Project Portfolio</title><style>{_styles()}</style></head><body>
<header class='top'><div class='brand'><span class='brand-mark'>◇</span>LATTICE</div><nav class='nav'><span><strong>Projects</strong> <b>{portfolio.get('active_projects',0)}/{portfolio.get('active_projects',0)}</b></span><span>Active <b>{portfolio.get('in_flight',0)}</b></span><span class='agent-nav'>Agents <b>{all_agents}</b></span><span>v{_safe(RELEASE)}</span><span class='principal'>P</span></nav></header>
<main><section class='portfolio-title'><h1>Project Portfolio</h1><p>Live state across active work. Detail stays inside each project.</p></section>{flash_html}
<section class='metrics'><article class='metric'><span>Active projects</span><strong>{portfolio.get('active_projects',0)}</strong><small>currently in portfolio</small></article><article class='metric'><span>Active / assigned agents</span><strong>{all_agents}</strong><small>across all projects</small></article><article class='metric'><span>Managed exceptions</span><strong>{managed_exceptions}</strong><small>remaining delegated</small></article><article class='metric'><span>Accepted changes</span><strong>{len(changes)}</strong><small>recent durable changes</small></article></section>
{_decision_strip(inbox)}
<section><div class='section-title'><h2>Active Projects</h2><span>{portfolio.get('in_flight',0)} currently executing · {portfolio.get('pending_verification',0)} awaiting verification</span></div><div class='project-grid'>{''.join(cards) or '<div class="empty-row">No active projects.</div>'}</div></section>
</main></body></html>"""


def render_project_html(model: dict, project_id: str) -> str:
    project = next((p for p in model.get("projects") or [] if str(p["project"]["id"]) == project_id), None)
    if project is None:
        return "<!doctype html><html><body><p>Project not found.</p></body></html>"
    meta = project["project"]
    objective = project.get("objective") or {}
    milestone = project.get("current_milestone") or project.get("milestone") or {}
    milestones = project.get("milestones") or []
    graph = project.get("consequence_graph") or {}
    evidence = project.get("evidence_chain") or []
    truths = project.get("frontier_truths") or []
    exceptions = project.get("open_exceptions") or []
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{_safe(meta['name'])} · Lattice</title><style>{_styles()}</style></head><body><header class='top'><div class='brand'><span class='brand-mark'>◇</span>LATTICE</div><nav class='nav'><span>v{_safe(RELEASE)}</span><span class='principal'>P</span></nav></header><main class='detail-shell'><a class='back' href='/'>← Project portfolio</a><h1>{_safe(meta['name'])}</h1><p class='objective'>{_safe(objective.get('title') or 'Objective complete')} · {_safe(milestone.get('title') or 'No milestone recorded')}</p><section class='detail-card'><h2>Milestones</h2><div class='detail-list'>{''.join(f"<div><strong>{_safe(m.get('ordinal'))}. {_safe(m.get('title'))}</strong> · {_safe(str(m.get('status') or '').title())}</div>" for m in milestones) or 'No milestones recorded.'}</div></section><section class='detail-card'><h2>Live agents</h2><div class='agents'>{_agent_table(project)}</div></section><section class='detail-card'><h2>Current frontier</h2><div class='detail-list'>{''.join(f"<div><strong>{_safe(a.get('role'))}</strong> · {_safe(a.get('title'))} · {_safe(a.get('kind'))}</div>" for a in (project.get('frontier') or [])) or 'No ready actions.'}</div></section><section class='detail-card'><h2>Exceptions and evidence</h2><div class='detail-list'><strong>{len(exceptions)}</strong> open exceptions · <strong>{len(evidence)}</strong> evidence records · <strong>{len(truths)}</strong> frontier truths · <strong>{sum((graph.get('counts') or {}).values())}</strong> consequence entities</div></section></main></body></html>"""
