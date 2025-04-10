from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.models.models import JobTracker  # Make sure to import your JobTracker model


class JobTrackerService:
    def __init__(self, db: Session):
        self.db = db

    def create_job_entry(self, job_data: dict) -> int:
        """
        Create a new job tracker entry and return the job_id.
        """
        try:
            job = JobTracker(**job_data)
            self.db.add(job)
            self.db.commit()
            self.db.refresh(job)
            return job.id
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def update_status(self, job_id: int, new_status: str):
        """
        Update the status of a job (pending, cancelled, completed).
        """
        try:
            job = self.db.query(JobTracker).filter(JobTracker.id == job_id).first()
            if not job:
                return None
            job.status = new_status
            self.db.commit()
            self.db.refresh(job)
            return job
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def add_remark(self, job_id: int, remark: str):
        """
        Add or update the remark for a job.
        """
        try:
            job = self.db.query(JobTracker).filter(JobTracker.id == job_id).first()
            if not job:
                return None
            job.remark = remark
            self.db.commit()
            self.db.refresh(job)
            return job
        except SQLAlchemyError:
            self.db.rollback()
            raise
    
    def get_all_jobs(self):
        """
        Retrieve all job tracker entries from the database.
        """
        try:
            return self.db.query(JobTracker).order_by(JobTracker.created_at.desc()).all()
        except SQLAlchemyError:
            self.db.rollback()
            raise
        
    def get_job_by_id(self, job_id: int):
        """
        Retrieve a specific job tracker entry by its ID.
        """
        try:
            job = self.db.query(JobTracker).filter(JobTracker.id == job_id).first()
            return job
        except SQLAlchemyError:
            self.db.rollback()
            raise