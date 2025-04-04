from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from database.models.models import (
    LinkedInProfile,
    LinkedInEducation,
    LinkedInPosition,
    LinkedInFullPosition,
    CompanyProfile
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
    
    def create_company_profile(self, company_data: dict):
        """Creates and saves a new CompanyProfile entry in the database."""
        company_dict = {
        "id": int(company_data.get("id", 0)),  # Convert ID to integer if needed
        "username": company_data.get("username"),
        "name": company_data.get("name"),
        "universal_name": company_data.get("universalName"),
        "linkedin_url": company_data.get("linkedinUrl"),
        "tagline": company_data.get("tagline"),
        "description": company_data.get("description"),
        "phone": company_data.get("phone"),
        "website": company_data.get("website"),
        "crunchbase_url": company_data.get("crunchbaseUrl", ""),
        "logo": company_data.get("Images", {}).get("logo"),
        "cover": company_data.get("Images", {}).get("cover"),
        "staff_count": company_data.get("staffCount"),
        "staff_count_range": company_data.get("staffCountRange"),
        "follower_count": company_data.get("followerCount"),
        "industries": company_data.get("industries", []),  # Ensure JSON format
        "founded_year": company_data.get("founded", {}).get("year"),
        "headquarter_country": company_data.get("headquarter", {}).get("country"),
        "headquarter_city": company_data.get("headquarter", {}).get("city"),
        "headquarter_postal_code": company_data.get("headquarter", {}).get("postalCode"),
        "headquarter_address_line1": company_data.get("headquarter", {}).get("line1"),
        "headquarter_address_line2": company_data.get("headquarter", {}).get("line2"),
            }
        new_company = CompanyProfile(**company_dict)
        self.db.add(new_company)
        self.db.commit()
        self.db.refresh(new_company)
        return new_company
    
    def get_company_by_username(self, username: str):
        """Fetch a company profile by username."""
        return self.db.query(CompanyProfile).filter(CompanyProfile.username == username).first()