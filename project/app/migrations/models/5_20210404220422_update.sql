-- upgrade --
CREATE TABLE IF NOT EXISTS "session" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "start_time" TIMESTAMPTZ,
    "event_id" VARCHAR(255) NOT NULL,
    "student_id" BIGINT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    "tutor_id" BIGINT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
-- downgrade --
DROP TABLE IF EXISTS "session";
