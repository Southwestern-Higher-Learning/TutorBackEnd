-- upgrade --
CREATE TABLE IF NOT EXISTS "report" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "type" SMALLINT NOT NULL,
    "reference_id" BIGINT NOT NULL,
    "reason" VARCHAR(200) NOT NULL,
    "description" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "user_id" BIGINT NOT NULL UNIQUE REFERENCES "user" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "report"."type" IS 'user: 0';;
CREATE TABLE IF NOT EXISTS "review" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "rating" INT NOT NULL,
    "content" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "reviewer_id" BIGINT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    "reviewee_id" BIGINT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_review_reviewe_fa7630" UNIQUE ("reviewer_id", "reviewee_id")
);;
-- downgrade --
DROP TABLE IF EXISTS "report";
DROP TABLE IF EXISTS "review";
