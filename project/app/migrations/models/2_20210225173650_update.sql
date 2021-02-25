-- upgrade --
CREATE TABLE IF NOT EXISTS "category" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(30) NOT NULL UNIQUE,
    "locked" BOOL NOT NULL  DEFAULT False,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);;
ALTER TABLE "user" DROP CONSTRAINT IF EXISTS "uid_user_first_n_2d121b";
ALTER TABLE "user" DROP CONSTRAINT IF EXISTS "uid_user_last_na_3c4ee3";
CREATE TABLE IF NOT EXISTS "user_categories" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "category_id" BIGINT NOT NULL REFERENCES "category" ("id") ON DELETE CASCADE,
    "user_id" BIGINT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_user_catego_user_id_60ab14" UNIQUE ("user_id", "category_id")
);;
CREATE TABLE "user_gategories" ("user_id" BIGINT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,"category_id" BIGINT NOT NULL REFERENCES "category" ("id") ON DELETE CASCADE);;
-- downgrade --
DROP TABLE IF EXISTS "user_gategories";
ALTER TABLE "user" ADD CONSTRAINT "uid_user_first_n_2d121b" UNIQUE ("first_name");
ALTER TABLE "user" ADD CONSTRAINT "uid_user_last_na_3c4ee3" UNIQUE ("last_name");
DROP TABLE IF EXISTS "category";
DROP TABLE IF EXISTS "user_categories";
