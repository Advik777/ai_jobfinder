

⚡️ AI Resume Matcher & Career Roadmap Generator

Turn your resume into real opportunities — and a clear path to get there.

🚀 Overview

This project is a full-stack AI system that:

📄 Understands your resume

🔎 Finds real internship listings

🧠 Intelligently ranks them using embeddings

📊 Shows exactly where you stand

🧭 Builds a personalized roadmap to close your skill gaps

All of this runs locally — no API keys required.

🧠 Core Idea

Most job platforms tell you what you qualify for.

This project tells you:

What you're missing — and exactly how to fix it.

🔥 Features

📄 Resume Intelligence

Upload a PDF resume

Extracts and analyzes text

Detects technical skills automatically

🔎 AI Job Matching

Scrapes real listings from:

Indeed

ZipRecruiter

Glassdoor

Uses semantic embeddings (nomic-embed-text)

Ranks using cosine similarity + FAISS

💡 Output per job:

Match score

Matched skills

Missing skills

🧭 Roadmap Generator (Game-Changer)

Save any job → Generate a personalized skill roadmap using Llama 3.1 8B

Each roadmap includes:

🚨 Missing skills (High / Medium / Low priority)

📚 Learning resources (courses, docs, books, practice)

⏳ Time estimates per skill

💼 Experience gap suggestions

✍️ Clean 2-line summary

🔐 Fully Local AI Stack

No OpenAI / paid APIs

Runs entirely via Ollama

Privacy-friendly + cost-free

⚙️ Tech Stack

🖥️ Frontend

Next.js

Tailwind CSS

Built using Claude Code

⚡ Backend

Python

FastAPI

🤖 AI / ML

LLM: Llama 3.1 8B (Ollama)

Embeddings: nomic-embed-text (768-dim)

Vector DB: FAISS

📊 Data Layer

Job scraping: python-jobspy

PDF parsing: pdfplumber

Database: SQLite
