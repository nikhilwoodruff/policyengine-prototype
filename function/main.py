import functions_framework
import os
import json
from flask import Request, Response
from policyengine import Simulation
from supabase import create_client, Client
import datetime
import traceback
import plotly.graph_objects as go

# Initialize Supabase client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


@functions_framework.http
def main(request: Request):
    """HTTP Cloud Function that runs a PolicyEngine simulation.

    Args:
        request (flask.Request): The request object containing simulation parameters

    Returns:
        The response text, or any set of values that can be turned into a
        flask.Response object using `make_response`
    """
    # Set CORS headers for the preflight request
    if request.method == "OPTIONS":
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for 3600s
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "3600",
        }
        return ("", 204, headers)

    # Set CORS headers for the main request
    headers = {"Access-Control-Allow-Origin": "*"}

    try:
        request_json = request.get_json(silent=True)
        if not request_json:
            return (
                json.dumps(
                    {
                        "status": "error",
                        "message": "You must pass in valid JSON.",
                    }
                ),
                400,
                headers,
            )

        job_id = request_json.get("job_id")

        if not job_id:
            return (
                json.dumps(
                    {
                        "status": "error",
                        "message": "You must pass in a job_id.",
                    }
                ),
                400,
                headers,
            )

        run_compute(job_id)

        return (json.dumps({"status": "success"}), 200, headers)

    except Exception as e:
        # Log error and update simulation record if it exists
        error_message = str(e)

        return (
            json.dumps({"status": "error", "message": error_message}),
            500,
            headers,
        )


def run_compute(job_id):
    print(f"Running job {job_id}")
    # Supabase. Get job with job id and print options

    job = supabase.table("job").select("*").eq("id", job_id).execute()

    if len(job.data) == 0:
        return

    job = job.data[0]

    # Set job status to running

    supabase.table("job").update(
        {
            "status": "running",
            "started_at": datetime.datetime.now().isoformat(),
        }
    ).eq("id", job_id).execute()

    try:
        options = job["options"]
        path = options.pop("path")
        kwargs = options.pop("kwargs", {})
        simulation = Simulation(
            **options,
        )
        print(path)
        result = simulation.calculate(path or "/", **kwargs)
        result = safe_json_decode(result)

        # Set job status to complete and fill result

        supabase.table("job").update(
            {"status": "complete", "result": result}
        ).eq("id", job_id).execute()

    except Exception as e:
        # Set job status to error and fill error

        supabase.table("job").update(
            {"status": "error", "result": {"error": traceback.format_exc()}}
        ).eq("id", job_id).execute()

    print(f"Completed job {job_id}")


def safe_json_decode(data):
    # Decode JSON data, cast all float-like values to python float (e.g. no float32)

    def _safe_json_decode(data):
        if isinstance(data, dict):
            return {
                key: _safe_json_decode(value) for key, value in data.items()
            }
        if isinstance(data, go.Figure):
            return data.to_json()
        if isinstance(data, list):
            return [_safe_json_decode(item) for item in data]
        if not isinstance(data, str):
            try:
                return float(data)
            except ValueError:
                return data
        return data

    return _safe_json_decode(data)
