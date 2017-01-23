PRAGMA encoding = "UTF-8";
PRAGMA foreign_keys = ON;

-- A configuration for the System-Under-Test (SUT).
--
-- This should have a name, and be accompanied by an optional description.
-- For example:
--
--  native -- All services are run as native Linux processes.
--  docker -- All services are run within seperate Docker containers.
--  ssl    -- As with native, but with SSL/TLS enabled.
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
    id              PRIMARY KEY,
    configuration   TEXT REFERENCES configuration(name)
        ON DELETE CASCADE ON UPDATE CASCADE,
    experiment      TEXT REFERENCES experiment(name)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- The individual power samples for a particular run of an experiment.
--
-- The power samples are the root mean square (RMS) watts recorded for a one
-- second sampling period (1Hz).
CREATE TABLE IF NOT EXISTS measurement(
    run             REFERENCES run(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    timestamp       REAL NOT NULL, -- Unix timestamp in milliseoncds
    power           REAL NOT NULL
);

-- Estimates the energy given the power measurements. This denormalizes the
-- database a little bit, but makes it easier to share the computed data with
-- external programs.
CREATE TABLE IF NOT EXISTS energy(
    id              PRIMARY KEY REFERENCES run(id),
    configuration   TEXT REFERENCES configuration(name)
        ON DELETE CASCADE ON UPDATE CASCADE,
    experiment      TEXT REFERENCES experiment(name)
        ON DELETE CASCADE ON UPDATE CASCADE,
    energy          REAL NOT NULL,
    started         REAL NOT NULL,
    ended           REAL NOT NULL,
    elapsed_time    REAL NOT NULL
);
