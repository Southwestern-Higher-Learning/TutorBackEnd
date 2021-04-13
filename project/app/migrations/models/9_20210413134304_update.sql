-- upgrade --
ALTER TABLE "report" DROP CONSTRAINT IF EXISTS "fk_report_user_9b7f3fe3";
ALTER TABLE "report" DROP COLUMN "user_id";
-- downgrade --
ALTER TABLE "report" ADD "user_id" BIGINT NOT NULL;
ALTER TABLE "report" ADD CONSTRAINT "fk_report_user_9b7f3fe3" FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE CASCADE;
