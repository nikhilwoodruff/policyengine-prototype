from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client
import requests
import json
import os
from datetime import datetime
from typing import Optional, Dict
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import traceback

# Initialize FastAPI app
app = FastAPI()

origins = [
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase client

# Cloud Function URL

if not os.getenv("LOCAL"):
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    cloud_function_url = os.getenv("CLOUD_FUNCTION_URL")
else:
    cloud_function_url = os.getenv("CLOUD_FUNCTION_LOCAL_URL")
    supabase_url = os.getenv("SUPABASE_LOCAL_URL")
    supabase_key = os.getenv("SUPABASE_LOCAL_KEY")

print(supabase_url, os.getenv("LOCAL"))

supabase = create_client(supabase_url, supabase_key)


# Pydantic model for job creation request
class JobCreate(BaseModel):
    options: Dict


# Pydantic model for job response
class Job(BaseModel):
    id: int
    created_at: datetime
    status: str
    result: Optional[Dict] = None
    options: Dict
    started_at: Optional[datetime] = None


@app.get("/api/hello")
async def main():
    return {"message": "Hello World"}


@app.post("/api/job", response_model=Job)
async def create_job(job: JobCreate):
    print(job)
    try:
        # Insert job into Supabase
        print("Inserting new job into table")
        new_job = (
            supabase.table("job")
            .insert(
                {
                    "status": "pending",
                    "options": job.options,
                    "result": None,
                    "started_at": None,
                }
            )
            .execute()
        )

        print(new_job)

        if not new_job.data:
            raise HTTPException(status_code=500, detail="Failed to create job")

        created_job = new_job.data[0]

        # Trigger Cloud Function using requests
        try:
            if os.getenv("LOCAL"):
                # Find a better way of debugging cloud functions locally, this doesn't mock the full process
                from tasks.simulate.run_compute import run_compute

                print("Running compute locally for", created_job["id"])
                run_compute(created_job["id"])
            else:
                requests.post(
                    cloud_function_url,
                    json={"job_id": created_job["id"]},
                    timeout=0.1,  # 0.1 second timeout
                )
        except requests.exceptions.RequestException as e:
            # Log the error but don't fail the job creation
            print(f"Failed to trigger cloud function: {str(e)}")
            # Optionally update job status to indicate trigger failure
            supabase.table("job").update({"status": "trigger_failed"}).eq(
                "id", created_job["id"]
            ).execute()

        return Job(**created_job)

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/job/{job_id}", response_model=Job)
async def get_job(job_id: int):
    try:
        job = supabase.table("job").select("*").eq("id", job_id).execute()

        if not job.data:
            raise HTTPException(status_code=404, detail="Job not found")

        return Job(**job.data[0])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
