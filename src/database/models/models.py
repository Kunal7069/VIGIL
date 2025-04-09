from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, JSON,Text, Enum, Float,LargeBinary
from sqlalchemy.sql import func
from database.config.config import Base
from sqlalchemy.orm import relationship
import enum


class ActivityComments(Base):
    __tablename__ = "activity_comments"  # Renamed to use underscores

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False, index=True)
    
    # Author info
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    headline = Column(String(300), nullable=True)
    profile_url = Column(String(300), nullable=False)

    # Post info
    post_text = Column(Text, nullable=False)
    highlighted_comment = Column(Text, nullable=True)
    post_url = Column(String(300), nullable=False, unique=True)

    # Reaction counts
    total_reactions = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    appreciation_count = Column(Integer, default=0)
    empathy_count = Column(Integer, default=0)
    praise_count = Column(Integer, default=0)
    funny_count = Column(Integer, default=0)

    # Engagement counts
    comments_count = Column(Integer, default=0)
    reposts_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    commentors = relationship("ActivityCommentsCommentor", back_populates="activity_comment", cascade="all, delete-orphan")
    reactors = relationship("ActivityCommentsReactor", back_populates="activity_comment", cascade="all, delete-orphan")
    media = relationship("ActivityCommentsMedia", back_populates="activity_comment", cascade="all, delete-orphan")
    videos = relationship("ActivityCommentsVideo", back_populates="activity_comment", cascade="all, delete-orphan")


class ActivityCommentsCommentor(Base):
    __tablename__ = "activity_comments_commentors"  # Renamed to use underscores

    id = Column(Integer, primary_key=True, index=True)
    activity_comment_id = Column(Integer, ForeignKey("activity_comments.id"), nullable=False)  # Fixed table reference
    name = Column(String(100))
    linkedin_url = Column(String(500))
    title = Column(String(300))
    text = Column(Text)

    activity_comment = relationship("ActivityComments", back_populates="commentors")


class ActivityCommentsReactor(Base):
    __tablename__ = "activity_comments_reactors"  # Renamed to use underscores

    id = Column(Integer, primary_key=True, index=True)
    activity_comment_id = Column(Integer, ForeignKey("activity_comments.id"), nullable=False)  # Fixed table reference
    full_name = Column(String(100))
    headline = Column(String(300))
    reaction_type = Column(String(50))
    profile_url = Column(String(500))

    activity_comment = relationship("ActivityComments", back_populates="reactors")

class ActivityCommentsMedia(Base):
    __tablename__ = "activity_comments_media"

    id = Column(Integer, primary_key=True, index=True)
    activity_comment_id = Column(Integer, ForeignKey("activity_comments.id"), nullable=False)
    url = Column(String(500), nullable=False)
    media_data = Column(LargeBinary, nullable=True) 
    width = Column(Integer)
    height = Column(Integer)

    activity_comment = relationship("ActivityComments", back_populates="media")


class ActivityCommentsVideo(Base):
    __tablename__ = "activity_comments_videos"

    id = Column(Integer, primary_key=True, index=True)
    activity_comment_id = Column(Integer, ForeignKey("activity_comments.id"), nullable=False)
    url = Column(String(500), nullable=False)
    poster = Column(String(500), nullable=False)
    duration = Column(Integer)

    activity_comment = relationship("ActivityComments", back_populates="videos")
    

class ActivityReactions(Base):
    __tablename__ = "Activity Reactions"

    id = Column(Integer, primary_key=True, index=True)
    
    # Profile we're tracking (activity is from this person's feed)
    username = Column(String(100), nullable=False, index=True)

    # Action info
    action = Column(String(300), nullable=False)

    # Post content
    post_text = Column(Text, nullable=False)
    post_url = Column(String(500), nullable=False, unique=True)

    # Author info
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    headline = Column(String(300), nullable=True)
    profile_url = Column(String(300), nullable=False)

    # Engagement data
    total_reactions = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    empathy_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    commentors = relationship("ActivityReactionsCommentor", back_populates="activity_reaction", cascade="all, delete-orphan")
    reactors = relationship("ActivityReactionsReactor", back_populates="activity_reaction", cascade="all, delete-orphan")

class ActivityReactionsCommentor(Base):
    __tablename__ = "Activity Reactions Commentors"

    id = Column(Integer, primary_key=True, index=True)
    activity_reaction_id = Column(Integer, ForeignKey("Activity Reactions.id"), nullable=False)
    name = Column(String(100))
    linkedin_url = Column(String(500))
    title = Column(String(300))
    text = Column(Text)

    activity_reaction = relationship("ActivityReactions", back_populates="commentors")

class ActivityReactionsReactor(Base):
    __tablename__ = "Activity Reactions Reactors"

    id = Column(Integer, primary_key=True, index=True)
    activity_reaction_id = Column(Integer, ForeignKey("Activity Reactions.id"), nullable=False)
    full_name = Column(String(100))
    headline = Column(String(300))
    reaction_type = Column(String(50))
    profile_url = Column(String(500))

    activity_reaction = relationship("ActivityReactions", back_populates="reactors")
    
class CompanyProfile(Base):
    __tablename__ = "Company Profile"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    universal_name = Column(String(255), unique=True, nullable=False)
    linkedin_url = Column(Text, nullable=False)
    tagline = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    website = Column(Text, nullable=True)
    crunchbase_url = Column(Text, nullable=True)

    # Image URLs
    logo = Column(Text, nullable=True)
    cover = Column(Text, nullable=True)

    # Company details
    staff_count = Column(Integer, nullable=True)
    staff_count_range = Column(String(50), nullable=True)
    follower_count = Column(Integer, nullable=True)

    # Industry and founding year
    industries = Column(JSON, nullable=True)  # Storing industries as an array
    founded_year = Column(Integer, nullable=True)

    # Headquarters details
    headquarter_country = Column(String(100), nullable=True)
    headquarter_city = Column(String(100), nullable=True)
    headquarter_postal_code = Column(String(20), nullable=True)
    headquarter_address_line1 = Column(String(255), nullable=True)
    headquarter_address_line2 = Column(String(255), nullable=True)

    # Timestamp
    created_at = Column(TIMESTAMP, server_default=func.now())

class LinkedInProfile(Base):
    __tablename__ = "Linked Profile"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    profile_picture = Column(Text, nullable=True)
    headline = Column(Text, nullable=True)

    geo_country = Column(String(100), nullable=True)
    geo_city = Column(String(100), nullable=True)
    geo_full = Column(String(200), nullable=True)
    geo_country_code = Column(String(10), nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    

class LinkedInEducation(Base):
    __tablename__ = "Linkedin Education"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False)  # FK alternative

    school_name = Column(String(200), nullable=True)
    degree = Column(String(200), nullable=True)
    field_of_study = Column(String(200), nullable=True)
    grade = Column(String(50), nullable=True)

    start_year = Column(Integer, nullable=True)
    start_month = Column(Integer, nullable=True)
    end_year = Column(Integer, nullable=True)
    end_month = Column(Integer, nullable=True)

    description = Column(Text, nullable=True)
    activities = Column(Text, nullable=True)
    url = Column(Text, nullable=True)
    school_id = Column(String(100), nullable=True)
    
class LinkedInPosition(Base):
    __tablename__ = "Linkedin Positions"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False)

    company_id = Column(Integer, nullable=True)
    company_name = Column(String(200), nullable=True)
    company_username = Column(String(200), nullable=True)
    company_url = Column(Text, nullable=True)

    industry = Column(String(200), nullable=True)
    staff_count = Column(String(50), nullable=True)

    title = Column(String(200), nullable=True)
    location = Column(String(200), nullable=True)
    employment_type = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)

    start_year = Column(Integer, nullable=True)
    start_month = Column(Integer, nullable=True)
    end_year = Column(Integer, nullable=True)
    end_month = Column(Integer, nullable=True)
    
class LinkedInFullPosition(Base):
    __tablename__ = "Linkedin Full Positions"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False)

    company_id = Column(Integer, nullable=True)
    company_name = Column(String(200), nullable=True)
    company_username = Column(String(200), nullable=True)
    company_url = Column(Text, nullable=True)

    industry = Column(String(200), nullable=True)
    staff_count = Column(String(50), nullable=True)

    title = Column(String(200), nullable=True)
    location = Column(String(200), nullable=True)
    employment_type = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)

    start_year = Column(Integer, nullable=True)
    start_month = Column(Integer, nullable=True)
    end_year = Column(Integer, nullable=True)
    end_month = Column(Integer, nullable=True)
    
    
class LinkedInPost(Base):
    __tablename__ = "Linkedin Posts"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(String(100), unique=True, nullable=True, index=True)  # extracted from postUrl
    username = Column(String(100), index=True, nullable=False)
    text = Column(Text, nullable=True)
    original_post_text =  Column(Text, nullable=True)
    share_url = Column(String(500), nullable=True)
    post_url = Column(String(500), unique=True, nullable=False)
    total_reactions = Column(Integer, default=0)
    total_comments = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    media = relationship("LinkedInPostMedia", back_populates="post", cascade="all, delete")
    video = relationship("LinkedInPostVideo", back_populates="post", cascade="all, delete")
    comments = relationship("LinkedInPostComment", back_populates="post", cascade="all, delete")
    reactions = relationship("LinkedInPostReaction", back_populates="post", cascade="all, delete")


class LinkedInPostMedia(Base):
    __tablename__ = "Linkedin Post Images"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("Linkedin Posts.id"), nullable=False)
    url = Column(String(500), nullable=False)
    media_data = Column(LargeBinary, nullable=True) 
    width = Column(Integer)
    height = Column(Integer)

    post = relationship("LinkedInPost", back_populates="media")
    
class LinkedInPostVideo(Base):
    __tablename__ = "Linkedin Post Video"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("Linkedin Posts.id"), nullable=False)
    url = Column(String(500), nullable=False)
    poster = Column(String(500), nullable=False)
    duration = Column(Integer)

    post = relationship("LinkedInPost", back_populates="video")


class LinkedInPostComment(Base):
    __tablename__ = "Linkedin Post Comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("Linkedin Posts.id"), nullable=False)
    name = Column(String(100))
    linkedin_url = Column(String(500))
    title = Column(String(300))
    text = Column(Text)

    post = relationship("LinkedInPost", back_populates="comments")


class LinkedInPostReaction(Base):
    __tablename__ = "Linkedin Post Reactions"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("Linkedin Posts.id"), nullable=False)
    full_name = Column(String(100))
    headline = Column(String(300))
    reaction_type = Column(String(50))
    profile_url = Column(String(500))

    post = relationship("LinkedInPost", back_populates="reactions")

    
class JobStatusEnum(str, enum.Enum):
    pending = "pending"
    cancelled = "cancelled"
    completed = "completed"


class JobTracker(Base):
    __tablename__ = "job_tracker"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False, index=True)
    type=  Column(String(100), nullable=False, index=True)
    activity_comments = Column(String(10), default="no")
    activity_reactions = Column(String(10), default="no")
    profile_info = Column(String(10), default="no")
    post_scrap = Column(String(10), default="no")
    post_comments = Column(String(10), default="no")
    post_reactions = Column(String(10), default="no")

    post_limit = Column(Integer, nullable=True)
    comment_limit = Column(Integer, nullable=True)
    reaction_limit = Column(Integer, nullable=True)

    status = Column(Enum(JobStatusEnum), default=JobStatusEnum.pending)
    remark = Column(Text, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
