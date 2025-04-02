from database.config.config import SessionLocal, engine
from database.models.models import Base  # Import Base from models
from database.services.activity_comments_service import ActivityCommentsService
from database.services.activity_reactions_service import ActivityReactionsService
from database.services.activity_profile_service import LinkedInProfileService
from database.services.activity_posts_service import ActivityPostService
from database.services.activity_job_tracker import JobTrackerService
# Create tables if they do not exist
Base.metadata.create_all(bind=engine)

# Start DB session
db = SessionLocal()

# Create services
activity_comments_service = ActivityCommentsService(db)
activity_reactions_service = ActivityReactionsService(db)
activity_profile_service = LinkedInProfileService(db)
activity_posts_service = ActivityPostService(db)
activity_job_track = JobTrackerService(db)

# Export services for use in other files
services = {
    "activity_comments_service": activity_comments_service,
    "activity_reactions_service":activity_reactions_service,
    "activity_profile_service":activity_profile_service,
    "activity_posts_service":activity_posts_service,
    "activity_job_track":activity_job_track
    
}

# Close session when script execution ends
def close_db():
    db.close()
