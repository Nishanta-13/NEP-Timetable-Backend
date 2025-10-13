/*
  Warnings:

  - A unique constraint covering the columns `[adminMail]` on the table `User` will be added. If there are existing duplicate values, this will fail.
  - Made the column `professorId` on table `User` required. This step will fail if there are existing NULL values in that column.

*/
-- AlterTable
ALTER TABLE "public"."User" ADD COLUMN     "professorBranch" TEXT,
ALTER COLUMN "professorId" SET NOT NULL;

-- CreateIndex
CREATE UNIQUE INDEX "User_adminMail_key" ON "public"."User"("adminMail");
