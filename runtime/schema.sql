PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS projects (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('active', 'paused', 'closed')),
  max_wip INTEGER NOT NULL CHECK (max_wip > 0),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS objectives (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES projects(id) ON UPDATE CASCADE ON DELETE CASCADE,
  title TEXT NOT NULL,
  description TEXT NOT NULL DEFAULT '',
  status TEXT NOT NULL CHECK (status IN ('active', 'satisfied', 'paused', 'cancelled')),
  priority INTEGER NOT NULL DEFAULT 50 CHECK (priority BETWEEN 0 AND 100),
  owner_role TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS one_active_objective_per_project
ON objectives(project_id) WHERE status = 'active';

CREATE TABLE IF NOT EXISTS milestones (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES projects(id) ON UPDATE CASCADE ON DELETE CASCADE,
  objective_id TEXT NOT NULL REFERENCES objectives(id) ON UPDATE CASCADE ON DELETE CASCADE,
  title TEXT NOT NULL,
  ordinal INTEGER NOT NULL DEFAULT 1,
  status TEXT NOT NULL CHECK (status IN ('planned', 'active', 'accepted', 'cancelled')),
  created_at TEXT NOT NULL,
  accepted_at TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS one_active_milestone_per_project
ON milestones(project_id) WHERE status = 'active';

CREATE UNIQUE INDEX IF NOT EXISTS one_planned_milestone_per_project
ON milestones(project_id) WHERE status = 'planned';

CREATE TABLE IF NOT EXISTS records (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES projects(id) ON UPDATE CASCADE ON DELETE CASCADE,
  key TEXT NOT NULL,
  kind TEXT NOT NULL CHECK (kind IN ('requirement', 'constraint', 'decision', 'artifact', 'risk', 'contract')),
  title TEXT NOT NULL,
  body TEXT NOT NULL DEFAULT '',
  status TEXT NOT NULL CHECK (status IN ('current', 'invalidated', 'superseded')),
  version INTEGER NOT NULL CHECK (version > 0),
  owner_role TEXT NOT NULL,
  source_ref TEXT,
  content_hash TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(project_id, key)
);

CREATE TABLE IF NOT EXISTS record_versions (
  record_id TEXT NOT NULL REFERENCES records(id) ON UPDATE CASCADE ON DELETE CASCADE,
  version INTEGER NOT NULL,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  status TEXT NOT NULL,
  source_ref TEXT,
  content_hash TEXT NOT NULL,
  changed_by TEXT NOT NULL,
  change_reason TEXT NOT NULL,
  created_at TEXT NOT NULL,
  PRIMARY KEY(record_id, version)
);

CREATE TABLE IF NOT EXISTS truths (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES projects(id) ON UPDATE CASCADE ON DELETE CASCADE,
  key TEXT NOT NULL,
  statement TEXT NOT NULL,
  epistemic_status TEXT NOT NULL CHECK (epistemic_status IN ('observed', 'accepted', 'contested', 'false', 'superseded', 'unknown')),
  attention_state TEXT NOT NULL CHECK (attention_state IN ('frontier', 'background', 'archived')),
  confidence REAL CHECK (confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0)),
  source_ref TEXT,
  material INTEGER NOT NULL DEFAULT 0 CHECK (material IN (0, 1)),
  version INTEGER NOT NULL CHECK (version > 0),
  created_by TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(project_id, key)
);

CREATE TABLE IF NOT EXISTS truth_versions (
  truth_id TEXT NOT NULL REFERENCES truths(id) ON UPDATE CASCADE ON DELETE CASCADE,
  version INTEGER NOT NULL,
  statement TEXT NOT NULL,
  epistemic_status TEXT NOT NULL,
  confidence REAL,
  source_ref TEXT,
  material INTEGER NOT NULL,
  changed_by TEXT NOT NULL,
  change_reason TEXT NOT NULL,
  created_at TEXT NOT NULL,
  PRIMARY KEY(truth_id, version)
);

CREATE TABLE IF NOT EXISTS truth_links (
  from_truth_id TEXT NOT NULL REFERENCES truths(id) ON UPDATE CASCADE ON DELETE CASCADE,
  to_truth_id TEXT NOT NULL REFERENCES truths(id) ON UPDATE CASCADE ON DELETE CASCADE,
  relation TEXT NOT NULL CHECK (relation IN ('supports', 'contradicts', 'refines', 'depends_on', 'supersedes')),
  created_by TEXT NOT NULL,
  created_at TEXT NOT NULL,
  PRIMARY KEY(from_truth_id, to_truth_id, relation),
  CHECK (from_truth_id <> to_truth_id)
);

CREATE TABLE IF NOT EXISTS truth_transitions (
  id TEXT PRIMARY KEY,
  truth_id TEXT NOT NULL REFERENCES truths(id) ON UPDATE CASCADE ON DELETE CASCADE,
  from_attention TEXT NOT NULL,
  to_attention TEXT NOT NULL,
  reason TEXT NOT NULL,
  changed_by TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS conditions (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES projects(id) ON UPDATE CASCADE ON DELETE CASCADE,
  objective_id TEXT NOT NULL REFERENCES objectives(id) ON UPDATE CASCADE ON DELETE CASCADE,
  milestone_id TEXT NOT NULL REFERENCES milestones(id) ON UPDATE CASCADE ON DELETE CASCADE,
  key TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  owner_role TEXT NOT NULL,
  verifier_role TEXT NOT NULL,
  priority INTEGER NOT NULL DEFAULT 50 CHECK (priority BETWEEN 0 AND 100),
  severity TEXT NOT NULL DEFAULT 'major' CHECK (severity IN ('critical', 'major', 'minor', 'note')),
  status TEXT NOT NULL CHECK (status IN ('unknown', 'unmet', 'candidate', 'satisfied', 'blocked', 'waived')),
  state_version INTEGER NOT NULL DEFAULT 1 CHECK (state_version > 0),
  attempt_count INTEGER NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
  attempt_budget INTEGER NOT NULL DEFAULT 3 CHECK (attempt_budget > 0),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(project_id, key),
  CHECK (owner_role <> verifier_role)
);

CREATE TABLE IF NOT EXISTS condition_inputs (
  condition_id TEXT NOT NULL REFERENCES conditions(id) ON UPDATE CASCADE ON DELETE CASCADE,
  record_id TEXT NOT NULL REFERENCES records(id) ON UPDATE CASCADE ON DELETE CASCADE,
  accepted_record_version INTEGER,
  PRIMARY KEY(condition_id, record_id)
);

CREATE TABLE IF NOT EXISTS condition_truths (
  condition_id TEXT NOT NULL REFERENCES conditions(id) ON UPDATE CASCADE ON DELETE CASCADE,
  truth_id TEXT NOT NULL REFERENCES truths(id) ON UPDATE CASCADE ON DELETE CASCADE,
  accepted_truth_version INTEGER,
  relevance TEXT NOT NULL DEFAULT '',
  PRIMARY KEY(condition_id, truth_id)
);

CREATE TABLE IF NOT EXISTS condition_dependencies (
  condition_id TEXT NOT NULL REFERENCES conditions(id) ON UPDATE CASCADE ON DELETE CASCADE,
  depends_on_condition_id TEXT NOT NULL REFERENCES conditions(id) ON UPDATE CASCADE ON DELETE CASCADE,
  accepted_state_version INTEGER,
  PRIMARY KEY(condition_id, depends_on_condition_id),
  CHECK (condition_id <> depends_on_condition_id)
);

CREATE TABLE IF NOT EXISTS condition_reviewers (
  condition_id TEXT NOT NULL REFERENCES conditions(id) ON UPDATE CASCADE ON DELETE CASCADE,
  role TEXT NOT NULL,
  review_kind TEXT NOT NULL CHECK (review_kind IN ('mandatory', 'primary')),
  PRIMARY KEY(condition_id, role)
);

CREATE TABLE IF NOT EXISTS submissions (
  id TEXT PRIMARY KEY,
  condition_id TEXT NOT NULL REFERENCES conditions(id) ON UPDATE CASCADE ON DELETE CASCADE,
  state_version INTEGER NOT NULL,
  attempt_no INTEGER NOT NULL,
  role TEXT NOT NULL,
  summary TEXT NOT NULL,
  artifact_refs_json TEXT NOT NULL DEFAULT '[]',
  evidence_ref TEXT,
  status TEXT NOT NULL CHECK (status IN ('pending', 'accepted', 'rejected', 'superseded')),
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reviews (
  id TEXT PRIMARY KEY,
  submission_id TEXT NOT NULL REFERENCES submissions(id) ON UPDATE CASCADE ON DELETE CASCADE,
  role TEXT NOT NULL,
  review_kind TEXT NOT NULL CHECK (review_kind IN ('mandatory', 'primary')),
  verdict TEXT NOT NULL CHECK (verdict IN ('SATISFIED', 'NOT_SATISFIED', 'CONCUR', 'BLOCK')),
  summary TEXT NOT NULL,
  evidence_ref TEXT,
  created_at TEXT NOT NULL,
  UNIQUE(submission_id, role)
);

CREATE TABLE IF NOT EXISTS evidence (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES projects(id) ON UPDATE CASCADE ON DELETE CASCADE,
  entity_type TEXT NOT NULL,
  entity_id TEXT NOT NULL,
  role TEXT NOT NULL,
  summary TEXT NOT NULL,
  source_ref TEXT,
  content_hash TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS commitments (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES projects(id) ON UPDATE CASCADE ON DELETE CASCADE,
  title TEXT NOT NULL,
  detail TEXT NOT NULL DEFAULT '',
  owner_role TEXT NOT NULL,
  priority INTEGER NOT NULL DEFAULT 50 CHECK (priority BETWEEN 0 AND 100),
  due_at TEXT,
  blocking INTEGER NOT NULL DEFAULT 0 CHECK (blocking IN (0, 1)),
  status TEXT NOT NULL CHECK (status IN ('open', 'fulfilled', 'cancelled')),
  version INTEGER NOT NULL DEFAULT 1,
  created_by TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS exceptions (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES projects(id) ON UPDATE CASCADE ON DELETE CASCADE,
  dedupe_key TEXT NOT NULL,
  title TEXT NOT NULL,
  detail TEXT NOT NULL DEFAULT '',
  severity TEXT NOT NULL CHECK (severity IN ('critical', 'major', 'minor', 'note')),
  owner_role TEXT NOT NULL,
  principal_only INTEGER NOT NULL DEFAULT 0 CHECK (principal_only IN (0, 1)),
  target_type TEXT,
  target_id TEXT,
  status TEXT NOT NULL CHECK (status IN ('open', 'resolved', 'dismissed')),
  resolution TEXT,
  version INTEGER NOT NULL DEFAULT 1,
  raised_by TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS one_open_exception_per_key
ON exceptions(project_id, dedupe_key) WHERE status = 'open';

CREATE TABLE IF NOT EXISTS leases (
  id TEXT PRIMARY KEY,
  action_key TEXT NOT NULL UNIQUE,
  project_id TEXT NOT NULL REFERENCES projects(id) ON UPDATE CASCADE ON DELETE CASCADE,
  action_kind TEXT NOT NULL,
  target_id TEXT NOT NULL,
  role TEXT NOT NULL,
  leased_by TEXT NOT NULL,
  created_at TEXT NOT NULL,
  expires_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  revision INTEGER NOT NULL,
  project_id TEXT REFERENCES projects(id) ON UPDATE CASCADE ON DELETE CASCADE,
  event_type TEXT NOT NULL,
  entity_type TEXT NOT NULL,
  entity_id TEXT NOT NULL,
  role TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS conditions_by_frontier
ON conditions(project_id, milestone_id, status, priority);

CREATE INDEX IF NOT EXISTS leases_by_capacity
ON leases(project_id, role, expires_at);

CREATE INDEX IF NOT EXISTS truths_by_attention
ON truths(project_id, attention_state, epistemic_status);

CREATE INDEX IF NOT EXISTS events_by_project_revision
ON events(project_id, revision, id);
