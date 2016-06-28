PRAGMA encoding = "UTF-8";

CREATE TABLE configuration(
    name            TEXT PRIMARY KEY,
    description     TEXT
);

CREATE TABLE test(
    name            TEXT PRIMARY KEY,
    description     TEXT
);

CREATE TABLE run(
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    configuration   TEXT,   -- configuration.name
    test            TEXT,   -- test.name
    started         DATETIME NOT NULL
);

CREATE TABLE measurement(
    run             INTEGER, -- test_run.id
    timestamp       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    power           REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS measurement_run ON measurement (run);
