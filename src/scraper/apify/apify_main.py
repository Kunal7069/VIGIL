import os
from typing import List,Dict,Optional
from fastapi import FastAPI, HTTPException,APIRouter
from pydantic import BaseModel, Field, model_validator
from dotenv import load_dotenv
from scraper.apify.apify_manager.post_manager import ApifyScraper
from scraper.apify.model.apify_model import UsernameRequest
from database.main import services
# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()
router = APIRouter()
# Get Rapid API key from environment
APIFY_ACTOR_TOKEN = os.getenv("APIFY_ACTOR_TOKEN")
APIFY_API_KEY = os.getenv("APIFY_API_KEY")

apify_scraper= ApifyScraper(APIFY_API_KEY,APIFY_ACTOR_TOKEN)


@router.post("/get-activity-data")
async def get_activity_comments(req: UsernameRequest):
    try:
        profile_url = f"https://www.linkedin.com/in/{req.username}/recent-activity/all/"
        job_data = req.model_dump()
        job_data.pop("cookie", None)  # Safely remove the 'cookie' key if it exists
        job_id = services['activity_job_track'].create_job_entry(job_data)
        profiles_url=[]
        profiles_url.append(profile_url)
        cookies_as_json = [cookie.model_dump() for cookie in req.cookie]
        result = apify_scraper.scrape_profiles(profiles_url,cookies_as_json)
        services['activity_job_track'].update_status(job_id, "completed")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving comments: {str(e)}")