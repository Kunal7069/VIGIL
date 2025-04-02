from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from database.models.models import ActivityComments


class ActivityCommentsService:
    def __init__(self, db: Session):
        self.db = db

    def save_batch_activity_comments(self, comments_data: list[dict]):
        """
        Save a batch of activity comment records.
        - Avoid duplicates (by post_url)
        - Wrap in transaction with rollback on failure
        """
        inserted = []
        try:
            for data in comments_data:
                # Skip if post already exists (by post_url)
                exists = (
                    self.db.query(ActivityComments)
                    .filter(ActivityComments.post_url == data["post_url"])
                    .first()
                )
                if exists:
                    continue

                comment = ActivityComments(**data)
                self.db.add(comment)
                inserted.append(comment)

            self.db.commit()
            return inserted

        except (IntegrityError, SQLAlchemyError, Exception):
            self.db.rollback()
            raise

    def get_activity_comments_by_username(self, username: str):
        """
        Fetch all activity comments for a given LinkedIn username.
        """
        try:
            return (
                self.db.query(ActivityComments)
                .filter(ActivityComments.username == username)
                .order_by(ActivityComments.created_at.desc())
                .all()
            )
        except SQLAlchemyError:
            return []
