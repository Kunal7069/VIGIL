from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from database.models.models import LinkedInPost, LinkedInPostMedia, LinkedInPostComment, LinkedInPostReaction


class ActivityPostService:
    def __init__(self, db: Session):
        self.db = db

    def save_post_with_details(self, post_data: dict, username:str):
        """
        Save a single post with its comments, media, and reactions.
        Ensures all linked to the same post_id and username.
        """
        try:
            # Check if the post already exists
            existing = (
                self.db.query(LinkedInPost)
                .filter(LinkedInPost.post_url == post_data["postUrl"])
                .first()
            )
            if existing:
                return  # Post already exists, skip saving

            # Create and save post
            post = LinkedInPost(
                username=username,
                post_url=post_data.get("postUrl"),
                share_url=post_data.get("shareUrl"),
                text=post_data.get("text", ""),
                total_reactions=post_data.get("totalreactions", 0),
                total_comments=post_data.get("totalcomments", 0)
            )
            self.db.add(post)
            self.db.flush()  # Get post.id before commit

            # Save comments
            for comment in post_data.get("comments", []):
                self.db.add(LinkedInPostComment(
                    post_id=post.id,
                    name=comment.get("name", ""),
                    linkedin_url=comment.get("linkedinUrl", ""),
                    title=comment.get("title", ""),
                    text=comment.get("text", "")
                ))

            # Save media
            for media in post_data.get("media", []):
                self.db.add(LinkedInPostMedia(
                    post_id=post.id,
                    url=media.get("url"),
                    width=media.get("width"),
                    height=media.get("height")
                ))

            # Save reactions
            for reaction in post_data.get("reactions", []):
                self.db.add(LinkedInPostReaction(
                    post_id=post.id,
                    full_name=reaction.get("fullName", ""),
                    profile_url=reaction.get("profileUrl", ""),
                    headline=reaction.get("headline", ""),
                    reaction_type=reaction.get("reactionType", "")
                ))

            self.db.commit()

        except (IntegrityError, SQLAlchemyError, Exception):
            self.db.rollback()
            raise

    def get_posts_by_username(self, username: str):
        """
        Fetch all posts (with nested comments, media, and reactions) for a given username.
        """
        try:
            posts = (
                self.db.query(LinkedInPost)
                .filter(LinkedInPost.username == username)
                .all()
            )

            result = []
            for post in posts:
                result.append({
                    "post_id": post.id,
                    "text": post.text,
                    "post_url": post.post_url,
                    "share_url": post.share_url,
                    "total_reactions": post.total_reactions,
                    "total_comments": post.total_comments,
                    "comments": [
                        {
                            "name": c.name,
                            "linkedin_url": c.linkedin_url,
                            "title": c.title,
                            "text": c.text
                        }
                        for c in post.comments
                    ],
                    "media": [
                        {
                            "url": m.url,
                            "width": m.width,
                            "height": m.height
                        }
                        for m in post.media
                    ],
                    "reactions": [
                        {
                            "full_name": r.full_name,
                            "profile_url": r.profile_url,
                            "headline": r.headline,
                            "reaction_type": r.reaction_type
                        }
                        for r in post.reactions
                    ]
                })

            return result
        except SQLAlchemyError:
            return []
