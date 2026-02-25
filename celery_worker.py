from dotenv import load_dotenv
load_dotenv()

from celery import Celery
from datetime import datetime
import os
import traceback
import time

from crewai import Crew, Process
from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from task import analyze_financial_document as financial_analysis_task
from Database import SessionLocal, AnalysisJob, JobStatus

# ✅ Celery app using Redis as broker and backend
celery_app = Celery(
    "financial_analyzer",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    worker_concurrency=2,
)


@celery_app.task(bind=True, name="analyze_document_task")
def analyze_document_task(self, job_id: str, query: str, file_path: str):
    """
    Celery background task — processes PDF and saves result to DB
    """
    db = SessionLocal()

    try:
        # ✅ Update job status to processing
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        if job:
            job.status = JobStatus.PROCESSING
            job.updated_at = datetime.utcnow()
            db.commit()

        time.sleep(3)  # ✅ small delay to avoid rate limits

        # ✅ Run CrewAI crew
        financial_crew = Crew(
            agents=[verifier, financial_analyst, investment_advisor, risk_assessor],
            tasks=[financial_analysis_task],
            process=Process.sequential,
        )
        result = financial_crew.kickoff({'query': query, 'file_path': file_path})

        # ✅ Save completed result to DB
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        if job:
            job.status = JobStatus.COMPLETED
            job.result = str(result)
            job.updated_at = datetime.utcnow()
            db.commit()

        return {"status": "completed", "job_id": job_id}

    except Exception as e:
        # ✅ Save error to DB
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        if job:
            job.status = JobStatus.FAILED
            job.error = str(e)
            job.updated_at = datetime.utcnow()
            db.commit()
        traceback.print_exc()
        raise e

    finally:
        # ✅ Clean up uploaded file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        db.close()