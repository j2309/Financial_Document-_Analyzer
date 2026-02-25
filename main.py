from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
import os
import uuid
import traceback

from Database import create_tables, get_db, AnalysisJob, JobStatus
from celery_worker import analyze_document_task  # ✅ import Celery task

# ✅ Create database tables on startup
create_tables()

app = FastAPI(title="Financial Document Analyzer")


@app.get("/")
async def root():
    return {"message": "Financial Document Analyzer API is running"}


@app.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights"),
    db: Session = Depends(get_db)
):
    """Upload PDF → queues job in Redis/Celery → returns job_id instantly"""
    job_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{job_id}.pdf"

    try:
        os.makedirs("data", exist_ok=True)

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        if query is None or query.strip() == "":
            query = "Analyze this financial document for investment insights"

        # ✅ Save job to database
        job = AnalysisJob(
            id=job_id,
            status=JobStatus.PENDING,
            query=query.strip(),
            filename=file.filename,
        )
        db.add(job)
        db.commit()

        # ✅ Send to Celery queue — processes in background worker!
        analyze_document_task.delay(job_id, query.strip(), file_path)

        return {
            "status": "queued",
            "job_id": job_id,
            "message": "Analysis queued in Redis! Use /status/{job_id} to check progress."
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status/{job_id}")
async def get_status(job_id: str, db: Session = Depends(get_db)):
    """Check the status of your analysis job"""
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    response = {
        "job_id": job.id,
        "status": job.status,
        "query": job.query,
        "filename": job.filename,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }

    if job.status == JobStatus.COMPLETED:
        response["analysis"] = job.result
    elif job.status == JobStatus.FAILED:
        response["error"] = job.error

    return response


@app.get("/history")
async def get_history(db: Session = Depends(get_db)):
    """Get all past analysis jobs"""
    jobs = db.query(AnalysisJob).order_by(AnalysisJob.created_at.desc()).all()
    return {
        "total": len(jobs),
        "jobs": [
            {
                "job_id": job.id,
                "status": job.status,
                "query": job.query,
                "filename": job.filename,
                "created_at": job.created_at,
                "has_result": job.result is not None,
            }
            for job in jobs
        ]
    }


@app.delete("/job/{job_id}")
async def delete_job(job_id: str, db: Session = Depends(get_db)):
    """Delete a job from the database"""
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    return {"message": f"Job {job_id} deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)