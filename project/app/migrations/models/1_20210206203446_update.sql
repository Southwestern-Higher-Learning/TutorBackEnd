-- upgrade --
ALTER TABLE "credentials" ALTER COLUMN "json_field" DROP NOT NULL;
-- downgrade --
ALTER TABLE "credentials" ALTER COLUMN "json_field" SET NOT NULL;
