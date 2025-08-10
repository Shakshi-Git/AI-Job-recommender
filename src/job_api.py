# C:\Job\src\job_api.py
from apify_client import ApifyClient
import os
from dotenv import load_dotenv

load_dotenv()

ACTOR_ID = os.getenv("APIFY_LINKEDIN_ACTOR_ID", "BHzefUZlZRKWxkTck")
__all__ = ["fetch_linkedin_jobs"]  # makes intent explicit for 'from ... import ...'


def fetch_linkedin_jobs(search_query: str, location: str = "India", rows: int = 60):
    """
    Fetch LinkedIn jobs using the Apify actor.

    NOTE: We intentionally create the Apify client INSIDE this function so that
    importing this module never fails (even if tokens are missing).
    """
    api_token = os.getenv("APIFY_API_TOKEN")
    if not api_token:
        raise RuntimeError("APIFY_API_TOKEN is not set. Put it in your .env or environment.")

    client = ApifyClient(api_token)

    run_input = {
        "title": search_query,
        "location": location,
        "rows": rows,
        "sortby": "relevance",
        "freshness": "all",
        "experience": "all",
        "proxy": {"useApifyProxy": True, "apifyProxyGroups": ["RESIDENTIAL"]},
    }

    run = client.actor(ACTOR_ID).call(run_input=run_input)
    dataset_id = run.get("defaultDatasetId") or run.get("defaultDatasetID")
    if not dataset_id:
        raise RuntimeError("Apify run did not return a dataset ID.")

    jobs = list(client.dataset(dataset_id).iterate_items())
    return jobs
