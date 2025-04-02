from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from database.models.models import ActivityReactions


class ActivityReactionsService:
    def __init__(self, db: Session):
        self.db = db

    def save_batch_activity_reactions(self, posts_data: list[dict]):
        """
        Save a batch of activity post records.
        - Avoid duplicates (by post_url)
        - Wrap in transaction with rollback on failure
        """
        inserted = []
        try:
            for data in posts_data:
                # Skip if post already exists (by post_url)
                exists = (
                    self.db.query(ActivityReactions)
                    .filter(ActivityReactions.post_url == data["post_url"])
                    .first()
                )
                if exists:
                    continue

                post = ActivityReactions(**data)
                self.db.add(post)
                inserted.append(post)

            self.db.commit()
            return inserted

        except (IntegrityError, SQLAlchemyError, Exception):
            self.db.rollback()
            raise

    def get_activity_reactions_by_username(self, username: str):
        """
        Fetch all activity posts for a given LinkedIn username.
        """
        try:
            return (
                self.db.query(ActivityReactions)
                .filter(ActivityReactions.username == username)
                .order_by(ActivityReactions.created_at.desc())
                .all()
            )
        except SQLAlchemyError:
            return []
