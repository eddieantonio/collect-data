INSERT INTO configuration(name, description) VALUES
    ('native', 'Services running as processes in Linux'),
    ('docker', 'Services running in docker containers');

INSERT INTO test(name, description) VALUES
    ('idle', 'Have the server do nothing for 60 minutes');

INSERT INTO run(configuration, test, started, ended) VALUES
    ('native', 'idle', datetime('now', 'utc', '-2.0 seconds'), datetime('now', 'utc')),
    ('docker', 'idle', datetime('now', 'utc', '-2.0 seconds'), datetime('now', 'utc'));

INSERT INTO measurement(run, timestamp, power) VALUES
    ((SELECT id from run WHERE configuration = 'native' LIMIT 1), datetime('now', '-2.0 seconds'), 90.0),
    ((SELECT id from run WHERE configuration = 'native' LIMIT 1), datetime('now', '-1.0 second'), 89.9),
    ((SELECT id from run WHERE configuration = 'native' LIMIT 1), datetime('now', 'utc'), 90.1),

    ((SELECT id from run WHERE configuration = 'docker' LIMIT 1), datetime('now', '-2.0 seconds'), 90.1),
    ((SELECT id from run WHERE configuration = 'docker' LIMIT 1), datetime('now', '-1.0 second'), 90.3),
    ((SELECT id from run WHERE configuration = 'docker' LIMIT 1), datetime('now', 'utc'), 90.2);
