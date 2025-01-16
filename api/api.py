from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client
import requests
import json
import os
from datetime import datetime
from typing import Optional, Dict

# Initialize FastAPI app
app = FastAPI()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)

# Cloud Function URL
cloud_function_url = os.getenv("CLOUD_FUNCTION_URL")

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

@app.post("/jobs/", response_model=Job)
async def create_job(job: JobCreate):
    try:
        # Insert job into Supabase
        new_job = supabase.table("job").insert({
            "status": "pending",
            "options": job.options,
            "result": None,
            "started_at": None
        }).execute()
        
        if not new_job.data:
            raise HTTPException(status_code=500, detail="Failed to create job")
        
        created_job = new_job.data[0]
        
        # Trigger Cloud Function using requests
        try:
            response = requests.post(
                cloud_function_url,
                json={
                    "job_id": created_job["id"],
                    "options": created_job["options"]
                },
                timeout=10  # 10 second timeout
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            # Log the error but don't fail the job creation
            print(f"Failed to trigger cloud function: {str(e)}")
            # Optionally update job status to indicate trigger failure
            supabase.table("job").update({
                "status": "trigger_failed"
            }).eq("id", created_job["id"]).execute()
        
        return Job(**created_job)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs/{job_id}", response_model=Job)
async def get_job(job_id: int):
    try:
        job = supabase.table("job").select("*").eq("id", job_id).execute()
        
        if not job.data:
            raise HTTPException(status_code=404, detail="Job not found")
            
        return Job(**job.data[0])
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))