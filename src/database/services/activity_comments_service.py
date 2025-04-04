from sqlalchemy.orm import Session,joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from database.models.models import ActivityComments,ActivityCommentsCommentor,ActivityCommentsReactor

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

                # Extract commentors and reactors separately
                commentors_data = data.pop("commentors", [])
                reactors_data = data.pop("reactors", [])

                comment = ActivityComments(**data)
                self.db.add(comment)
                self.db.flush()  # Get comment ID before inserting related data

                # Insert commentors
                for commentor in commentors_data:
                    new_commentor = ActivityCommentsCommentor(
                        activity_comment_id=comment.id,
                        name=commentor.get("name"),
                        linkedin_url=commentor.get("linkedinUrl"),
                        title=commentor.get("title"),
                        text=commentor.get("text")
                    )
                    self.db.add(new_commentor)

                # Insert reactors
                for reactor in reactors_data:
                    new_reactor = ActivityCommentsReactor(
                        activity_comment_id=comment.id,
                        full_name=reactor.get("fullName"),
                        headline=reactor.get("headline"),
                        reaction_type=reactor.get("reactionType"),
                        profile_url=reactor.get("profileUrl")
                    )
                    self.db.add(new_reactor)

                inserted.append(comment)

            self.db.commit()
            return inserted

        except (IntegrityError, SQLAlchemyError, Exception):
            self.db.rollback()
            raise

    
    def get_activity_comments_by_username(self, username: str):
        """
        Fetch all activity comments for a given LinkedIn username, including related commentors and reactors.
        """
        try:
            return (
                self.db.query(ActivityComments)
                .filter(ActivityComments.username == username)
                .options(
                    joinedload(ActivityComments.commentors),  # Ensures related data is preloaded
                    joinedload(ActivityComments.reactors)
                )
                .order_by(ActivityComments.created_at.desc())
                .all()
            )
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return []
