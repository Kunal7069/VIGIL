from sqlalchemy.orm import Session,joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from database.models.models import ActivityReactions,ActivityReactionsCommentor,ActivityReactionsReactor


class ActivityReactionsService:
    def __init__(self, db: Session):
        self.db = db

    
    def save_batch_activity_reactions(self, posts_data: list[dict]):
        """
        Save a batch of activity post records along with commentors and reactors.
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

                # Create the activity reaction entry
                post = ActivityReactions(
                    username=data["username"],
                    action=data["action"],
                    post_text=data["post_text"],
                    post_url=data["post_url"],
                    first_name=data["first_name"],
                    last_name=data["last_name"],
                    headline=data["headline"],
                    profile_url=data["profile_url"],
                    total_reactions=data["total_reactions"],
                    like_count=data["like_count"],
                    empathy_count=data["empathy_count"],
                    comments_count=data["comments_count"]
                )

                self.db.add(post)
                self.db.flush()  # Get the post ID before committing

                # Add commentors
                for commentor in data.get("commentors", []):
                    new_commentor = ActivityReactionsCommentor(
                        activity_reaction_id=post.id,
                        name=commentor["name"],
                        linkedin_url=commentor["linkedinUrl"],
                        title=commentor["title"],
                        text=commentor["text"]
                    )
                    self.db.add(new_commentor)

                # Add reactors
                for reactor in data.get("reactors", []):
                    new_reactor = ActivityReactionsReactor(
                        activity_reaction_id=post.id,
                        full_name=reactor["fullName"],
                        headline=reactor["headline"],
                        reaction_type=reactor["reactionType"],
                        profile_url=reactor["profileUrl"]
                    )
                    self.db.add(new_reactor)

                inserted.append(post)

            self.db.commit()
            return inserted

        except (IntegrityError, SQLAlchemyError, Exception):
            self.db.rollback()
            raise

    
    def get_activity_reactions_by_username(self, username: str):
        """
        Fetch all activity posts for a given LinkedIn username including reactors and commentors.
        """
        try:
            return (
                self.db.query(ActivityReactions)
                .filter(ActivityReactions.username == username)
                .options(
                    joinedload(ActivityReactions.commentors),
                    joinedload(ActivityReactions.reactors)
                )
                .order_by(ActivityReactions.created_at.desc())
                .all()
            )
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return []