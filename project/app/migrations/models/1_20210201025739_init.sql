-- upgrade --
ALTER TABLE "textsummary" ADD "description" TEXT NOT NULL;
-- downgrade --
ALTER TABLE "textsummary" DROP COLUMN "description";
