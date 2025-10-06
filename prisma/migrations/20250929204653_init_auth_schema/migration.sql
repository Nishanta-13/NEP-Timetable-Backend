-- CreateEnum
CREATE TYPE "public"."Role" AS ENUM ('Student', 'Professor', 'Admin');

-- CreateTable
CREATE TABLE "public"."User" (
    "id" TEXT NOT NULL,
    "role" "public"."Role" NOT NULL DEFAULT 'Student',
    "abcId" TEXT,
    "studentId" TEXT,
    "email" TEXT NOT NULL,
    "professorId" TEXT,
    "professorMail" TEXT,
    "passwordHash" TEXT,
    "name" TEXT NOT NULL,
    "adminId" TEXT,
    "adminMail" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "User_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "User_abcId_key" ON "public"."User"("abcId");

-- CreateIndex
CREATE UNIQUE INDEX "User_studentId_key" ON "public"."User"("studentId");

-- CreateIndex
CREATE UNIQUE INDEX "User_email_key" ON "public"."User"("email");

-- CreateIndex
CREATE UNIQUE INDEX "User_professorId_key" ON "public"."User"("professorId");

-- CreateIndex
CREATE UNIQUE INDEX "User_professorMail_key" ON "public"."User"("professorMail");

-- CreateIndex
CREATE UNIQUE INDEX "User_adminId_key" ON "public"."User"("adminId");

-- CreateIndex
CREATE UNIQUE INDEX "User_adminMail_key" ON "public"."User"("adminMail");
