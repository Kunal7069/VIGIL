from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from database.models.models import (
    LinkedInProfile,
    LinkedInEducation,
    LinkedInPosition,
    LinkedInFullPosition
)


class LinkedInProfileService:
    def __init__(self, db: Session):
        self.db = db

    def save_profile_bundle(self, profile_data: dict):
        """
        Saves profile, educations, positions, and full_positions to DB.
        All inserts are transactional. Rolls back on failure.
        """
        username = profile_data.get("username")
        if not username:
            raise ValueError("Username is required in profile data")

        try:
            # --- Save basic profile ---
            existing_profile = (
                self.db.query(LinkedInProfile)
                .filter(LinkedInProfile.username == username)
                .first()
            )
            if not existing_profile:
                new_profile = LinkedInProfile(
                    username=username,
                    first_name=profile_data.get("first_name"),
                    last_name=profile_data.get("last_name"),
                    profile_picture=profile_data.get("profile_picture"),
                    headline=profile_data.get("headline"),
                    geo_country=profile_data.get("geo", {}).get("country"),
                    geo_city=profile_data.get("geo", {}).get("city"),
                    geo_full=profile_data.get("geo", {}).get("full"),
                    geo_country_code=profile_data.get("geo", {}).get("countryCode")
                )
                self.db.add(new_profile)

                # --- Save Educations ---
            
                for edu in profile_data.get("educations", []):
                    self.db.add(LinkedInEducation(
                        username=username,
                        school_name=edu.get("school_name"),
                        degree=edu.get("degree"),
                        field_of_study=edu.get("field_of_study"),
                        grade=edu.get("grade"),
                        start_year=edu.get("start", {}).get("year"),
                        start_month=edu.get("start", {}).get("month"),
                        end_year=edu.get("end", {}).get("year"),
                        end_month=edu.get("end", {}).get("month"),
                        description=edu.get("description"),
                        activities=edu.get("activities"),
                        url=edu.get("url"),
                        school_id=edu.get("school_id")
                    ))

                # --- Save Positions ---
                for pos in profile_data.get("positions", []):
                    self.db.add(LinkedInPosition(
                        username=username,
                        company_id=pos.get("company_id"),
                        company_name=pos.get("company_name"),
                        company_username=pos.get("company_username"),
                        company_url=pos.get("company_url"),
                        industry=pos.get("industry"),
                        staff_count=pos.get("staff_count"),
                        title=pos.get("title"),
                        location=pos.get("location"),
                        employment_type=pos.get("employment_type"),
                        description=pos.get("description"),
                        start_year=pos.get("start", {}).get("year"),
                        start_month=pos.get("start", {}).get("month"),
                        end_year=pos.get("end", {}).get("year"),
                        end_month=pos.get("end", {}).get("month")
                    ))

                # --- Save Full Positions ---
                for pos in profile_data.get("full_positions", []):
                    self.db.add(LinkedInFullPosition(
                        username=username,
                        company_id=pos.get("company_id"),
                        company_name=pos.get("company_name"),
                        company_username=pos.get("company_username"),
                        company_url=pos.get("company_url"),
                        industry=pos.get("industry"),
                        staff_count=pos.get("staff_count"),
                        title=pos.get("title"),
                        location=pos.get("location"),
                        employment_type=pos.get("employment_type"),
                        description=pos.get("description"),
                        start_year=pos.get("start", {}).get("year"),
                        start_month=pos.get("start", {}).get("month"),
                        end_year=pos.get("end", {}).get("year"),
                        end_month=pos.get("end", {}).get("month")
                    ))

            self.db.commit()

        except (IntegrityError, SQLAlchemyError, Exception):
            self.db.rollback()
            raise

    def get_profile_by_username(self, username: str):
        return (
            self.db.query(LinkedInProfile)
            .filter(LinkedInProfile.username == username)
            .first()
        )

    def get_educations_by_username(self, username: str):
        return (
            self.db.query(LinkedInEducation)
            .filter(LinkedInEducation.username == username)
            .all()
        )

    def get_positions_by_username(self, username: str):
        return (
            self.db.query(LinkedInPosition)
            .filter(LinkedInPosition.username == username)
            .all()
        )

    def get_full_positions_by_username(self, username: str):
        return (
            self.db.query(LinkedInFullPosition)
            .filter(LinkedInFullPosition.username == username)
            .all()
        )
