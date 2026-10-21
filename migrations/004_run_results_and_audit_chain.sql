ALTER TABLE runs ADD COLUMN result_json TEXT;
ALTER TABLE audit_events ADD COLUMN previous_hash TEXT;
ALTER TABLE audit_events ADD COLUMN event_hash TEXT;
