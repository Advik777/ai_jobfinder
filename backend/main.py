import uuid
import json
import httpx
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import asyncio

from db import init_db, save_resume, get_resume, save_roadmap, get_roadmaps, delete_roadmap
from parser import extract_text
from skills import extract_skills
from scraper import fetch_jobs
from matcher import rank_jobs

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

OLLAMA_URL = "http://localhost:11434"
status_store: dict[str, str] = {}


@app.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    content = await file.read()
    text = extract_text(content)
    skills = extract_skills(text)
    resume_id = str(uuid.uuid4())[:8]
    save_resume(resume_id, text, skills)
    return {
        "resume_id": resume_id,
        "extracted_skills": skills,
        "resume_text": text[:500],
    }


@app.get("/status/{resume_id}")
def get_status(resume_id: str):
    return {"status": status_store.get(resume_id, "idle")}


@app.post("/search")
async def search_jobs(body: dict):
    resume_id = body.get("resume_id")
    location = body.get("location", "Remote")
    limit = int(body.get("limit", 20))

    resume = get_resume(resume_id)
    if not resume:
        return {"error": "Resume not found"}

    import json as jsonlib
    skills = jsonlib.loads(resume["skills"])

    async def stream():
        status_store[resume_id] = "scraping"
        yield json.dumps({"status": "scraping"}) + "\n"
        await asyncio.sleep(0.1)

        jobs = fetch_jobs(skills, location, limit)
        if not jobs:
            yield json.dumps({"status": "error", "message": "No jobs found"}) + "\n"
            return

        status_store[resume_id] = "embedding"
        yield json.dumps({"status": "embedding", "count": len(jobs)}) + "\n"
        await asyncio.sleep(0.1)

        status_store[resume_id] = "ranking"
        ranked = rank_jobs(resume["text"], jobs)

        status_store[resume_id] = "done"
        yield json.dumps({"status": "ranking"}) + "\n"

        for job in ranked:
            yield json.dumps(job) + "\n"
            await asyncio.sleep(0.05)

    return StreamingResponse(stream(), media_type="application/x-ndjson")


@app.post("/roadmap/generate")
async def generate_roadmap(body: dict):
    resume_id = body.get("resume_id")
    job_title = body.get("job_title")
    company = body.get("company")
    job_description = body.get("job_description", "")[:1500]
    job_url = body.get("job_url", "")

    resume = get_resume(resume_id)
    if not resume:
        return {"error": "Resume not found"}

    import json as jsonlib
    resume_skills = jsonlib.loads(resume["skills"])
    resume_snippet = resume["text"][:800]

    prompt = f"""You are a career advisor. Analyze the gap between this candidate's 
profile and the job, then return a JSON roadmap.

Job: {job_title} at {company}
Job description: {job_description}
Candidate's current skills: {", ".join(resume_skills)}
Candidate's resume: {resume_snippet}

Return ONLY a JSON object in this exact format, nothing else:
{{
  "missing_skills": [
    {{
      "skill": "skill name",
      "importance": "high" | "medium" | "low",
      "reason": "one sentence why this skill matters for the job",
      "resources": [
        {{"name": "resource name", "url": "https://...", "type": "course" | "docs" | "book" | "practice"}}
      ],
      "estimated_weeks": 2
    }}
  ],
  "experience_gaps": [
    {{
      "gap": "what experience is missing",
      "suggestion": "how to get it"
    }}
  ],
  "summary": "2 sentence overall assessment"
}}

Return only the JSON, no markdown, no explanation."""

    try:
        r = httpx.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": "llama3.1:8b",
                "messages": [{"role": "user", "content": prompt}],
                "stream": False
            },
            timeout=120
        )
        raw = r.json()["message"]["content"].strip()
        clean = raw.replace("```json", "").replace("```", "").strip()
        roadmap_data = jsonlib.loads(clean)

        save_roadmap(resume_id, job_title, company,
                     job_description, job_url, roadmap_data)

        return {"roadmap": roadmap_data, "job_title": job_title, "company": company}
    except Exception as e:
        print(f"Roadmap error: {e}")
        return {"error": str(e)}


@app.get("/roadmap/{resume_id}")
def get_roadmap_list(resume_id: str):
    import json as jsonlib
    rows = get_roadmaps(resume_id)
    result = []
    for row in rows:
        result.append({
            "id": row["id"],
            "job_title": row["job_title"],
            "company": row["company"],
            "job_url": row["job_url"],
            "roadmap": jsonlib.loads(row["roadmap_json"]),
            "created_at": row["created_at"],
        })
    return {"roadmaps": result}


@app.delete("/roadmap/{roadmap_id}")
def remove_roadmap(roadmap_id: int):
    delete_roadmap(roadmap_id)
    return {"deleted": roadmap_id}
    