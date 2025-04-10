from fastapi import FastAPI, Depends, HTTPException,APIRouter
from sqlalchemy.orm import Session
from typing import List
from database.main import services
from settings.rapid_api_management import rapid_api_management
# from settings.price_management import price_management
from scraper.rapid_api.model.rapid_model import SearchPostsRequest
from scraper.rapid_api.model.rapid_model import ActivityRequest
from pydantic import BaseModel
import http.client
import json
import os
from dotenv import load_dotenv
from math import ceil

load_dotenv()

RAPID_API_KEY = os.getenv("RAPID_API_KEY")

app = FastAPI()

router = APIRouter()

@router.get("/activity-comments/{username}")
def get_activity_comments(username: str):
    data= services['activity_comments_service'].get_activity_comments_by_username(username)
    return data

@router.get("/activity-reactions/{username}")
def get_activity_reactions(username: str):
    data= services['activity_reactions_service'].get_activity_reactions_by_username(username)
    return data

@router.get("/profile/{username}")
def get_profile(username: str):
    data= services['activity_profile_service'].get_profile_by_username(username)
    return data

@router.get("/company/{username}")
def get_profile(username: str):
    data= services['activity_profile_service'].get_company_by_username(username)
    return data

@router.get("/education/{username}")
def get_education(username: str):
    data= services['activity_profile_service'].get_educations_by_username(username)
    return data

@router.get("/positions/{username}")
def get_positions(username: str):
    data= services['activity_profile_service'].get_positions_by_username(username)
    return data

@router.get("/full-time-positions/{username}")
def get_full_time_positions(username: str):
    data= services['activity_profile_service'].get_full_positions_by_username(username)
    return data

@router.get("/posts/{username}")
def get_posts(username: str):
    data= services['activity_posts_service'].get_posts_by_username(username)
    return data

@router.get("/job-tracker")
def job_tracker():
    data= services['activity_job_track'].get_all_jobs()
    return data

    
@router.post("/search-posts")
def search_posts(request: SearchPostsRequest):
    """
    Searches LinkedIn posts using a keyword and fetches the specified number of posts using pagination.
    
    :param keyword: The keyword to search for.
    :param num_posts: The total number of posts to fetch.
    :return: A list of posts matching the keyword.
    """
    
    conn = http.client.HTTPSConnection(rapid_api_management.BASE_URL)
    
    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": rapid_api_management.BASE_URL,
        "Content-Type": "application/json"
    }

    collected_posts = []
    page = 1

    while len(collected_posts) < request.num_posts:
        payload = json.dumps({
            "keyword": request.keyword,
            "sortBy": "date_posted",
            "datePosted": "",
            "page": page,
            "contentType": "",
            "fromMember": [],
            "fromCompany": [],
            "mentionsMember": [],
            "mentionsOrganization": [],
            "authorIndustry": [],
            "authorCompany": [],
            "authorTitle": ""
        })

        conn.request("POST", "/search-posts", body=payload, headers=headers)
        res = conn.getresponse()
        data = res.read()

        try:
            response_json = json.loads(data.decode("utf-8"))
            posts = response_json.get("data", {}).get("items", [])
            
            if not posts:
                break  # Stop if no more posts are available

            collected_posts.extend(posts)

            if len(collected_posts) >= request.num_posts:
                break  # Stop if we've collected enough posts

            page += 1  # Move to the next page

        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Failed to decode API response")

    return {"total_fetched": len(collected_posts), "posts": collected_posts[:request.num_posts]}

@router.post("/credit-estimation")
def credit_estimation(req: ActivityRequest):
    from settings.price_management import price_management

    total_credits = 0
    p = price_management
    
    if req.type == "company":
        if req.profile_info == "yes":
            # Add 1 credit for enabling post_scrap
            total_credits += p.PROFILE_CREDIT
        
        if req.post_scrap == "yes":
            # Add credits for the number of posts to be scraped (batches of 50)
            post_batches = ceil(req.post_limit / p.POSTS_BATCH)
            total_credits += post_batches * p.POSTS_CREDIT

            if req.post_comments == "yes":
                # Add 1 credit per post to get commenters
                total_credits += req.post_limit * p.COMMENTORS_CREDIT

            if req.post_reactions == "yes":
                for _ in range(req.post_limit):
                    reactors = req.reaction_limit
                    if reactors <= p.REACTORS_BATCH:
                        total_credits += p.WITHOUT_POST_URL_REACTORS_CREDIT_1
                    else:
                        remaining = reactors - p.REACTORS_BATCH
                        batches = ceil(remaining / p.REACTORS_BATCH)
                        total_credits += p.WITHOUT_POST_URL_REACTORS_CREDIT_1 + (batches * p.WITHOUT_POST_URL_REACTORS_CREDIT_2)

    if req.type == "person":
        if req.profile_info == "yes":
            # Add 1 credit for enabling post_scrap
            total_credits += p.PROFILE_CREDIT
        
        if req.post_scrap == "yes":
            # Add credits for the number of posts to be scraped (batches of 50)
            post_batches = ceil(req.post_limit / p.POSTS_BATCH)
            total_credits += post_batches * p.POSTS_CREDIT

            if req.post_comments == "yes":
                # Add 1 credit per post to get commenters
                total_credits += req.post_limit * p.COMMENTORS_CREDIT

            if req.post_reactions == "yes":
                for _ in range(req.post_limit):
                    reactors = req.reaction_limit
                    if reactors <= p.REACTORS_BATCH:
                        total_credits += p.POST_URL_REACTORS_CREDIT_1
                    else:
                        remaining = reactors - p.REACTORS_BATCH
                        batches = ceil(remaining / p.REACTORS_BATCH)
                        total_credits += p.POST_URL_REACTORS_CREDIT_1 + (batches * p.POST_URL_REACTORS_CREDIT_2)
        
        if req.activity_comments == "yes":
    
            # Add credits for the number of posts to be scraped (batches of 50)
            total_credits += p.ACTIVITY_COMMENTS_CREDIT

            if req.post_comments == "yes":
                # Add 1 credit per post to get commenters
                total_credits += req.post_limit * p.COMMENTORS_CREDIT

            if req.post_reactions == "yes":
                for _ in range(req.post_limit):
                    reactors = req.reaction_limit
                    if reactors <= p.REACTORS_BATCH:
                        total_credits += p.WITHOUT_POST_URL_REACTORS_CREDIT_1
                    else:
                        remaining = reactors - p.REACTORS_BATCH
                        batches = ceil(remaining / p.REACTORS_BATCH)
                        total_credits += p.WITHOUT_POST_URL_REACTORS_CREDIT_1 + (batches * p.WITHOUT_POST_URL_REACTORS_CREDIT_2)
        
        if req.activity_reactions == "yes":

            # Add credits for the number of posts to be scraped (batches of 50)
            activity_reactions_batches = ceil(req.post_limit / p.ACTIVITY_REACTIONS_BATCH)
            total_credits += activity_reactions_batches * p.ACTIVITY_REACTIONS_CREDIT


            if req.post_comments == "yes":
                # Add 1 credit per post to get commenters
                total_credits += req.post_limit * p.COMMENTORS_CREDIT

            if req.post_reactions == "yes":
                for _ in range(req.post_limit):
                    reactors = req.reaction_limit
                    if reactors <= p.REACTORS_BATCH:
                        total_credits += p.POST_URL_REACTORS_CREDIT_1
                    else:
                        remaining = reactors - p.REACTORS_BATCH
                        batches = ceil(remaining / p.REACTORS_BATCH)
                        total_credits += p.POST_URL_REACTORS_CREDIT_1 + (batches * p.POST_URL_REACTORS_CREDIT_2)

    return {"total_credits": total_credits}