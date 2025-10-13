import express from "express";
import dotenv from "dotenv";
import cors from "cors";
import prisma from "./Controllers/prismaClient.js";
import authRoutes from "./Routes/auth.js";

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

app.use("/auth", authRoutes(prisma));

app.listen(4000, () => console.log("Server running on 4000"));
