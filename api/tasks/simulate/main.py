import functions_framework
import os
import json
from flask import Request, Response
from policyengine import Simulation
from supabase import create_client, Client
import datetime
import traceback
import plotly.graph_objects as go
from run_compute import safe_json_decode

# Initialize Supabase client

if not os.getenv("LOCAL"):
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
else:
    url: str = os.environ.get("SUPABASE_LOCAL_URL")
    key: str = os.environ.get("SUPABASE_LOCAL_KEY")
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
