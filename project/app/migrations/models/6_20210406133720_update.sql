-- upgrade --
ALTER TABLE "session" DROP CONSTRAINT IF EXISTS "fk_session_user_75250459";
COMMENT ON COLUMN "report"."type" IS 'user: 0
review: 1';
ALTER TABLE "session" DROP COLUMN "student_id";
CREATE TABLE IF NOT EXISTS "student_session" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "category_id" BIGINT NOT NULL REFERENCES "category" ("id") ON DELETE CASCADE,
    "session_id" BIGINT NOT NULL REFERENCES "session" ("id") ON DELETE CASCADE,
    "student_id" BIGINT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_student_ses_session_21f8c4" UNIQUE ("session_id", "student_id")
);;
CREATE TABLE IF NOT EXISTS "student_session" ("session_id" BIGINT NOT NULL REFERENCES "session" ("id") ON DELETE CASCADE,"user_id" BIGINT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE);;
-- downgrade --
DROP TABLE IF EXISTS "student_session";
COMMENT ON COLUMN "report"."type" IS 'user: 0';
ALTER TABLE "session" ADD "student_id" BIGINT NOT NULL;
DROP TABLE IF EXISTS "student_session";
ALTER TABLE "session" ADD CONSTRAINT "fk_session_user_75250459" FOREIGN KEY ("student_id") REFERENCES "user" ("id") ON DELETE CASCADE;
