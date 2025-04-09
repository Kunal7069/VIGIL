from sqlalchemy.orm import Session,joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from database.models.models import ActivityComments,ActivityCommentsCommentor,ActivityCommentsReactor,ActivityCommentsMedia,ActivityCommentsVideo
import requests
class ActivityCommentsService:
    def __init__(self, db: Session):
        self.db = db

    def save_main_comment(self, data: dict):
        """
        Save the main comment object and return it.
        """
        exists = (
            self.db.query(ActivityComments)
            .filter(ActivityComments.post_url == data["post_url"])
            .first()
        )
        if exists:
            return None


        # Save main comment
        comment = ActivityComments(**data)
        self.db.add(comment)
        self.db.flush()  # Get ID
        return comment

    def save_commentors(self, comment_id: int, commentors: list[dict]):
        for commentor in commentors:
            new_commentor = ActivityCommentsCommentor(
                activity_comment_id=comment_id,
                name=commentor.get("name"),
                linkedin_url=commentor.get("linkedinUrl"),
                title=commentor.get("title"),
                text=commentor.get("text")
            )
            self.db.add(new_commentor)

    def save_reactors(self, comment_id: int, reactors: list[dict]):
        for reactor in reactors:
            new_reactor = ActivityCommentsReactor(
                activity_comment_id=comment_id,
                full_name=reactor.get("fullName"),
                headline=reactor.get("headline"),
                reaction_type=reactor.get("reactionType"),
                profile_url=reactor.get("profileUrl")
            )
            self.db.add(new_reactor)

    def save_media(self, comment_id: int, media: list[dict],media_flag:str):
        for m in media:
            image_url = m.get("url")
            binary_data = None

            if media_flag == "yes" and image_url:
                try:
                    response = requests.get(image_url)
                    if response.status_code == 200:
                        binary_data = response.content
                except requests.RequestException:
                    pass  # Handle gracefully
            new_media = ActivityCommentsMedia(
                activity_comment_id=comment_id,
                url=m.get("url"),
                media_data=binary_data,
                width=m.get("width"),
                height=m.get("height")
            )
            self.db.add(new_media)

    def save_video(self, comment_id: int, video_data: list | dict):
        if isinstance(video_data, list):
            for video in video_data:
                new_video = ActivityCommentsVideo(
                    activity_comment_id=comment_id,
                    url=video.get("url"),
                    poster=video.get("poster"),
                    duration=video.get("duration"),
                )
                self.db.add(new_video)
        elif isinstance(video_data, dict):
            new_video = ActivityCommentsVideo(
                activity_comment_id=comment_id,
                url=video_data.get("url"),
                poster=video_data.get("poster"),
                duration=video_data.get("duration"),
            )
            self.db.add(new_video)
    
    def save_batch_activity_comments(self, comments_data: list[dict]):
        """
        Save a batch of activity comment records.
        - Avoid duplicates (by post_url)
        - Wrap in transaction with rollback on failure
        - Save associated commentors, reactors, media, and videos
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

                # Extract related data
                commentors_data = data.pop("commentors", [])
                reactors_data = data.pop("reactors", [])
                media_data = data.pop("media", [])
                video_data = data.pop("video", [])

                # Create main comment object
                comment = ActivityComments(**data)
                self.db.add(comment)
                self.db.flush()  # Assign ID before creating relationships

                # Add commentors
                for commentor in commentors_data:
                    new_commentor = ActivityCommentsCommentor(
                        activity_comment_id=comment.id,
                        name=commentor.get("name"),
                        linkedin_url=commentor.get("linkedinUrl"),
                        title=commentor.get("title"),
                        text=commentor.get("text")
                    )
                    self.db.add(new_commentor)

                # Add reactors
                for reactor in reactors_data:
                    new_reactor = ActivityCommentsReactor(
                        activity_comment_id=comment.id,
                        full_name=reactor.get("fullName"),
                        headline=reactor.get("headline"),
                        reaction_type=reactor.get("reactionType"),
                        profile_url=reactor.get("profileUrl")
                    )
                    self.db.add(new_reactor)

                # Add media
                for media in media_data:
                    new_media = ActivityCommentsMedia(
                        activity_comment_id=comment.id,
                        url=media.get("url"),
                        width=media.get("width"),
                        height=media.get("height"),
                        media_data=media.get("mediaData")  # Optional
                    )
                    self.db.add(new_media)

                # Add video (can be a list or dict depending on structure)
                if isinstance(video_data, list):
                    for video in video_data:
                        new_video = ActivityCommentsVideo(
                            activity_comment_id=comment.id,
                            url=video.get("url"),
                            poster=video.get("poster"),
                            duration=video.get("duration"),
                        )
                        self.db.add(new_video)
                elif isinstance(video_data, dict):  # If single video dict
                    new_video = ActivityCommentsVideo(
                        activity_comment_id=comment.id,
                        url=video_data.get("url"),
                        poster=video_data.get("poster"),
                        duration=video_data.get("duration"),
                    )
                    self.db.add(new_video)

                inserted.append(comment)

            self.db.commit()
            return inserted

        except (IntegrityError, SQLAlchemyError, Exception) as e:
            self.db.rollback()
            raise e
        
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
                    joinedload(ActivityComments.reactors),
                    joinedload(ActivityComments.media),
                    joinedload(ActivityComments.videos)
                )
                .order_by(ActivityComments.created_at.desc())
                .all()
            )
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return []
