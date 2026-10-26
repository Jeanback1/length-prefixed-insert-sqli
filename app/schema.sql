-- Lab schema. The application role can insert notes and read one demo row.
-- It is not a superuser and cannot run server programs.

CREATE TABLE secrets (
    id integer PRIMARY KEY,
    value text NOT NULL
);

CREATE TABLE notes (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    body text NOT NULL
);

INSERT INTO secrets (id, value) VALUES (1, 'lab-canary-7f3a');

CREATE USER app LOGIN PASSWORD 'app';
GRANT SELECT ON secrets TO app;
GRANT INSERT ON notes TO app;
GRANT USAGE, SELECT ON SEQUENCE notes_id_seq TO app;
