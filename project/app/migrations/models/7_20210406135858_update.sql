-- upgrade --
ALTER TABLE "student_session" DROP CONSTRAINT IF EXISTS "fk_student__user_390a85e3";
ALTER TABLE "student_session" RENAME COLUMN "student_id" TO "user_id";
ALTER TABLE "student_session" ADD CONSTRAINT "fk_student__user_ffa3f2d6" FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "student_session" DROP CONSTRAINT "fk_student__user_ffa3f2d6";
ALTER TABLE "student_session" RENAME COLUMN "user_id" TO "student_id";
ALTER TABLE "student_session" ADD CONSTRAINT "fk_student__user_390a85e3" FOREIGN KEY ("student_id") REFERENCES "user" ("id") ON DELETE CASCADE;
