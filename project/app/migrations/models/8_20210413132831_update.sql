-- upgrade --
ALTER TABLE "report" DROP CONSTRAINT IF EXISTS "uid_report_user_604e0f";
ALTER TABLE "report" DROP CONSTRAINT IF EXISTS "uid_report_user_id_6b8db0";
-- downgrade --
ALTER TABLE "report" ADD CONSTRAINT "uid_report_user_id_6b8db0" UNIQUE ("user_id");
ALTER TABLE "report" ADD CONSTRAINT "uid_report_user_604e0f" UNIQUE ("user");
