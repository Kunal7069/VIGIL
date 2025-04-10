import os
from fastapi import Depends,FastAPI, HTTPException,APIRouter, Header
from pydantic import BaseModel, Field, model_validator
from dotenv import load_dotenv
import json
from scraper.rapid_api.rapid_manager.activity_manager import LinkedInActivityFetcher
from scraper.rapid_api.rapid_manager.post_manager import LinkedinPostFetcher  
from scraper.rapid_api.rapid_manager.company_manager import CompanyPostFetcher
from scraper.rapid_api.model.rapid_model import ActivityRequest
from database.main import services
# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()
router = APIRouter()
# Get Rapid API key from environment
RAPID_API_KEY = os.getenv("RAPID_API_KEY")
linkedin = LinkedInActivityFetcher(RAPID_API_KEY)
post_fetcher = LinkedinPostFetcher(RAPID_API_KEY)
company_post_fetcher = CompanyPostFetcher(RAPID_API_KEY)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

async def verify_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer" or token != ACCESS_TOKEN:
            raise HTTPException(status_code=401, detail="Invalid or missing token")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")
    
def make_json_serializable(data):
    if isinstance(data, dict):
        return {k: make_json_serializable(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [make_json_serializable(v) for v in data]
    else:
        try:
            json.dumps(data)
            return data
        except TypeError:
            return str(data)  # Fallback: convert un-serializable objects to string
    
@router.post("/get-activity-data", dependencies=[Depends(verify_token)])
async def get_linkedin_data(req: ActivityRequest):
    response_data = {}
    try:
        print(req)
        data = req.model_dump()
        data.pop("media_flag", None)
        job_id = services['activity_job_track'].create_job_entry(data)
        print(job_id)

        if req.profile_info == "yes" and req.type=="person":
            response_data["profile"] = linkedin.extract_clean_user_profile(req.username, job_id)
        
        if req.profile_info == "yes" and req.type=="company":
            response_data["profile"] = linkedin.extract_clean_company_profile(req.username, job_id)

        if req.activity_comments == "yes":
            response_data["comments"] = linkedin.extract_comment_details(req.username,req.post_reactions,req.post_comments,req.post_limit,req.comment_limit,req.reaction_limit,job_id,req.media_flag)

        if req.activity_reactions == "yes":
            response_data["reactions"] = linkedin.extract_likes_details(req.username,req.post_reactions,req.post_comments,req.post_limit,req.comment_limit,req.reaction_limit ,job_id)

        if req.post_scrap == "yes" and req.type=="person":
            response_data["posts"] = post_fetcher.get_profile_posts(
                req.username,
                req.post_reactions,
                req.post_comments,
                req.post_limit,
                req.comment_limit,
                req.reaction_limit,
                req.media_flag,
                job_id
            )
            
        if req.post_scrap == "yes" and req.type=="company":
            print("COMPANY")
            response_data["posts"] = company_post_fetcher.get_company_posts(
                req.username,
                req.post_reactions,
                req.post_comments,
                req.post_limit,
                req.comment_limit,
                req.reaction_limit,
                req.media_flag,
                job_id
                
            )

        # Mark job as completed
        print("RESPONSE DATA", response_data)
        if isinstance(response_data, dict) and all(
            isinstance(v, dict) and 'error' in v for v in response_data.values()
        ):
            services['activity_job_track'].update_status(job_id, "cancelled")
        else:
            services['activity_job_track'].update_status(job_id, "completed")

        print("RETURN")
        return response_data

    except Exception as e:
        # On failure, mark job as cancelled and add remark
        services['activity_job_track'].update_status(job_id, "cancelled")
        print(e)
        raise HTTPException(status_code=500, detail=e)
        # return {"error": str(e)}
