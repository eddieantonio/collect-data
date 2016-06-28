PRAGMA encoding = "UTF-8";

CREATE TABLE IF NOT EXISTS configuration(
    name            TEXT PRIMARY KEY,
    description     TEXT
);

CREATE TABLE IF NOT EXISTS test(
    name            TEXT PRIMARY KEY,
    description     TEXT
);

CREATE TABLE IF NOT EXISTS run(
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    configuration   TEXT,   -- configuration.name
    test            TEXT    -- test.name
);

CREATE TABLE IF NOT EXISTS measurement(
    run             INTEGER, -- test_run.id
    timestamp       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    power           REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS measurement_run ON measurement (run);
