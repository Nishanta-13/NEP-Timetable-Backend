import express from "express";
import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";

export default function authRoutes(prisma) {
    const router = express.Router();
    
    router.post("/student/signup", async (req, res) => {
        try {
            const { name, email, password, studentId, abcId } = req.body;

            if (!name || !email || !password || !studentId)
                return res.status(400).json({ error: "Missing fields" });

            const existing = await prisma.user.findUnique({ where: { email } });
            if (existing) return res.status(400).json({ error: "Email already exists" });

            const hashed = await bcrypt.hash(password, 10);

            const student = await prisma.user.create({
                data: {
                    name,
                    email,
                    passwordHash: hashed,
                    role: "Student",
                    studentId,
                    abcId,
                },
            });

            res.json({ message: "Student registered", student });
        } catch (err) {
            res.status(400).json({ error: err.message });
        }
    });

    // ---------- STUDENT LOGIN ----------
    router.post("/student/login", async (req, res) => {
        try {
            const { email, password } = req.body;
            const user = await prisma.user.findUnique({ where: { email } });
            if (!user || user.role !== "Student") return res.status(400).json({ error: "Invalid credentials" });

            const ok = await bcrypt.compare(password, user.passwordHash);
            if (!ok) return res.status(400).json({ error: "Invalid credentials" });

            const token = jwt.sign({ id: user.id, role: user.role }, process.env.JWT_SECRET, { expiresIn: "2h" });
            res.json({ token, role: user.role });
        } catch (err) {
            res.status(400).json({ error: err.message });
        }
    });

    // ---------- PROFESSOR SIGNUP ----------
    router.post("/professor/signup", async (req, res) => {
        try {
            const { name, email, password, professorId, professorMail } = req.body;
            if (!name || !password || !professorMail || !professorId)
                return res.status(400).json({ error: "Missing fields" });

            const existing = await prisma.user.findUnique({ where: { professorMail } });
            if (existing) return res.status(400).json({ error: "Email already exists" });

            const hashed = await bcrypt.hash(password, 10);

            const professor = await prisma.user.create({
                data: {
                    name,
                    role: "Professor",
                    passwordHash: hashed,
                    professorId,
                    professorMail,
                    email, // optional main email
                },
            });

            res.json({ message: "Professor registered", professor });
        } catch (err) {
            res.status(400).json({ error: err.message });
        }
    });

    // ---------- PROFESSOR LOGIN ----------
    router.post("/professor/login", async (req, res) => {
        try {
            const { professorMail, password } = req.body;
            const user = await prisma.user.findUnique({ where: { professorMail } });
            if (!user || user.role !== "Professor") return res.status(400).json({ error: "Invalid credentials" });

            const ok = await bcrypt.compare(password, user.passwordHash);
            if (!ok) return res.status(400).json({ error: "Invalid credentials" });

            const token = jwt.sign({ id: user.id, role: user.role }, process.env.JWT_SECRET, { expiresIn: "2h" });
            res.json({ token, role: user.role });
        } catch (err) {
            res.status(400).json({ error: err.message });
        }
    });

    // ---------- ADMIN SIGNUP ----------
    router.post("/admin/signup", async (req, res) => {
        try {
            const { name, password, adminMail, adminId } = req.body;
            if (!name || !password || !adminMail || !adminId)
                return res.status(400).json({ error: "Missing fields" });

            const existing = await prisma.user.findUnique({ where: { adminMail } });
            if (existing) return res.status(400).json({ error: "Admin already exists" });

            const hashed = await bcrypt.hash(password, 10);

            const admin = await prisma.user.create({
                data: { name, passwordHash: hashed, role: "Admin", adminMail, adminId },
            });

            res.json({ message: "Admin registered", admin });
        } catch (err) {
            res.status(400).json({ error: err.message });
        }
    });

    // ---------- ADMIN LOGIN ----------
    router.post("/admin/login", async (req, res) => {
        try {
            const { adminMail, password } = req.body;
            const user = await prisma.user.findUnique({ where: { adminMail } });
            if (!user || user.role !== "Admin") return res.status(400).json({ error: "Invalid credentials" });

            const ok = await bcrypt.compare(password, user.passwordHash);
            if (!ok) return res.status(400).json({ error: "Invalid credentials" });

            const token = jwt.sign({ id: user.id, role: user.role }, process.env.JWT_SECRET, { expiresIn: "2h" });
            res.json({ token, role: user.role });
        } catch (err) {
            res.status(400).json({ error: err.message });
        }
    });
    router.get("/abc/login", (req, res) => {
        // For demo: redirect directly to callback
        res.redirect("/auth/abc/callback?code=demo123");
    });

    router.get("/abc/callback", async (req, res) => {
        try {
            // Fake ABC profile
            const fakeStudent = {
                abcId: "ABC2025DEMO01",
                studentId: "STU12345",
                name: "John Doe",
                email: "john.doe@univ.edu",
                credits: 78,
            };
            const student = await prisma.user.upsert({
                where: { abcId: fakeStudent.abcId },
                update: {
                    name: fakeStudent.name,
                    email: fakeStudent.email,
                    credits: fakeStudent.credits,
                },
                create: {
                    ...fakeStudent,
                    role: "Student",
                },
            });

            // Generate JWT token
            const token = jwt.sign(
                { id: student.id, role: student.role },
                process.env.JWT_SECRET,
                { expiresIn: "2h" }
            );

            // Redirect to frontend with token
            res.redirect(`${process.env.FRONTEND_URL}/dashboard?token=${token}`);
        } catch (err) {
            console.error(err);
            res.status(500).json({ error: "ABC login failed" });
        }
    });


    return router;
}
