-- upgrade --
ALTER TABLE "user" ADD "google_calendar_id" VARCHAR(255);
-- downgrade --
ALTER TABLE "user" DROP COLUMN "google_calendar_id";
