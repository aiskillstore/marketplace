-- CreateTable
CREATE TABLE "users" (
    "id" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "name" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "users_email_key" ON "users"("email");

-- AddColumn (example for altering existing table)
-- ALTER TABLE "users" ADD COLUMN "phone" TEXT;

-- CreateIndex (example for adding index to existing column)
-- CREATE INDEX "users_name_idx" ON "users"("name");

-- AddForeignKey
-- ALTER TABLE "posts" ADD CONSTRAINT "posts_user_id_fkey"
-- FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;
