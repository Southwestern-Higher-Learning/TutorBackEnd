-- upgrade --
CREATE TABLE IF NOT EXISTS "user" (
    "username" VARCHAR(20) NOT NULL UNIQUE,
    "password" VARCHAR(200),
    "is_active" BOOL NOT NULL  DEFAULT True,
    "is_superuser" BOOL NOT NULL  DEFAULT False,
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "email" VARCHAR(100) NOT NULL UNIQUE,
    "first_name" VARCHAR(100) NOT NULL UNIQUE,
    "last_name" VARCHAR(100) NOT NULL UNIQUE,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "profile_url" TEXT NOT NULL,
    "description" TEXT,
    "is_tutor" BOOL NOT NULL  DEFAULT False
);
COMMENT ON COLUMN "user"."password" IS 'Will auto hash with raw password when change';
CREATE TABLE IF NOT EXISTS "credentials" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "json_field" JSONB NOT NULL,
    "user_id" BIGINT NOT NULL UNIQUE REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(20) NOT NULL,
    "content" TEXT NOT NULL
);
