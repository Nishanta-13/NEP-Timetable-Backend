/*
  Warnings:

  - Changed the type of `role` on the `User` table. No cast exists, the column would be dropped and recreated, which cannot be done if there is data, since the column is required.
  - Made the column `abcId` on table `User` required. This step will fail if there are existing NULL values in that column.

*/
-- DropIndex
DROP INDEX "public"."User_adminId_key";

-- DropIndex
DROP INDEX "public"."User_adminMail_key";

-- DropIndex
DROP INDEX "public"."User_email_key";

-- DropIndex
DROP INDEX "public"."User_professorId_key";

-- DropIndex
DROP INDEX "public"."User_professorMail_key";

-- DropIndex
DROP INDEX "public"."User_studentId_key";

-- AlterTable
ALTER TABLE "public"."User" ADD COLUMN     "credits" INTEGER,
DROP COLUMN "role",
ADD COLUMN     "role" TEXT NOT NULL,
ALTER COLUMN "abcId" SET NOT NULL;
