CREATE TABLE IF NOT EXISTS transfer_state (
    id SERIAL PRIMARY KEY,
    last_created_at TIMESTAMP NOT NULL
);

INSERT INTO transfer_state (last_created_at)
SELECT '1970-01-01T00:00:00Z'
WHERE NOT EXISTS (SELECT 1 FROM transfer_state);
