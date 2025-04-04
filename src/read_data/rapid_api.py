from fastapi import FastAPI, Depends, HTTPException,APIRouter
from sqlalchemy.orm import Session
from typing import List
from database.main import services

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