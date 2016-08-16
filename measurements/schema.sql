PRAGMA encoding = "UTF-8";

-- A configuration for the System-Under-Test (SUT).
--
-- This should have a name, and be accompanied by an optional description.
-- For example:
--
--  native -- All services are run as native Linux processes.
--  docker -- All services are run within seperate Docker containers.
CREATE TABLE IF NOT EXISTS configuration(
    name            TEXT PRIMARY KEY,
    description     TEXT
);

-- An experiment that will be run on all configurations.
--
-- This should have a name, and be accompanied by an optional description.
-- For example:
--
--  idle -- Enable all services, but put no explict load on the system.
--  fullstack -- Run the Redis benchmark on the system.
CREATE TABLE IF NOT EXISTS experiment(
    name            TEXT PRIMARY KEY,
    description     TEXT
);

-- A particular run of an experiment.
--
-- This indicates the experiment itself and the hardware configuration of the
-- run.
--
-- The individual power measurements exist in `measurement`.
CREATE TABLE IF NOT EXISTS run(
    id              INTEGER PRIMARY KEY,
    configuration   TEXT,   -- configuration.name
    experiment      TEXT    -- experiment.name
);

-- The individual power samples for a particular run of an experiment.
--
-- The power samples are the root mean square (RMS) watts recorded for a one
-- second sampling period (1Hz).
CREATE TABLE IF NOT EXISTS measurement(
    run             INTEGER, -- test_run.id
    timestamp       REAL NOT NULL, -- Unix timestamp in milliseoncds
    power           REAL NOT NULL
);

-- Enables the sequential gathering of run data from the measurement table.
CREATE INDEX IF NOT EXISTS measurement_run ON measurement (run);
