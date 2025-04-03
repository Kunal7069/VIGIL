import os
from fastapi import FastAPI, HTTPException,APIRouter
from pydantic import BaseModel, Field, model_validator
from dotenv import load_dotenv
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

@router.post("/get-activity-data")
async def get_linkedin_data(req: ActivityRequest):
    response_data = {}
    try:
        print(req)
        job_id = services['activity_job_track'].create_job_entry(req.model_dump())
        print(job_id)

        if req.profile_info == "yes" and req.type=="person":
            response_data["profile"] = linkedin.extract_clean_user_profile(req.username, job_id)
        
        if req.profile_info == "yes" and req.type=="company":
            response_data["profile"] = linkedin.extract_clean_company_profile(req.username, job_id)

        if req.activity_comments == "yes":
            response_data["comments"] = linkedin.extract_comment_details(req.username, job_id)

        if req.activity_reactions == "yes":
            response_data["reactions"] = linkedin.extract_likes_details(req.username, job_id)

        if req.post_scrap == "yes" and req.type=="person":
            response_data["posts"] = post_fetcher.get_profile_posts(
                req.username,
                req.post_reactions,
                req.post_comments,
                req.post_limit,
            )
            
        if req.post_scrap == "yes" and req.type=="company":
            print("COMPANY")
            response_data["posts"] = company_post_fetcher.get_company_posts(
                req.username,
                req.post_reactions,
                req.post_comments,
                req.post_limit
                
            )

        # Mark job as completed
        services['activity_job_track'].update_status(job_id, "completed")
        return response_data

    except Exception as e:
        # On failure, mark job as cancelled and add remark
        services['activity_job_track'].update_status(job_id, "cancelled")
        raise HTTPException(status_code=500, detail="Failed to fetch LinkedIn activity data.")
