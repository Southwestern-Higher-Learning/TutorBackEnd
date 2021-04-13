-- upgrade --
ALTER TABLE "report" ADD "user_id" BIGINT NOT NULL;
ALTER TABLE "report" ADD CONSTRAINT "fk_report_user_9b7f3fe3" FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "report" DROP CONSTRAINT "fk_report_user_9b7f3fe3";
ALTER TABLE "report" DROP COLUMN "user_id";
