CREATE TABLE projects (
    project_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE runs (
    run_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(project_id),
    case_id TEXT,
    status TEXT NOT NULL CHECK (status IN (
        'created', 'validated', 'queued', 'running',
        'succeeded', 'failed', 'blocked', 'cancelled'
    )),
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE audit_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT REFERENCES projects(project_id),
    actor_id TEXT,
    event_type TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX runs_project_created_idx ON runs(project_id, created_at);
CREATE INDEX audit_project_created_idx ON audit_events(project_id, created_at);
