import functions_framework
import os
import json
import time
from policyengine import Simulation


@functions_framework.http
def run_simulation(request):
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
        
        if not request_json or "reform" not in request_json:
            return (json.dumps({"error": "Invalid request parameters"}), 400, headers)
        
        return (json.dumps({"success": "Yay"}), 400, headers)


    except Exception as e:
        # Log error and update simulation record if it exists
        error_message = str(e)
        
        return (json.dumps({
            "error": error_message
        }), 500, headers)
