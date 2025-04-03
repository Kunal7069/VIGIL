from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, JSON,Text, Enum, Float
from sqlalchemy.sql import func
from database.config.config import Base
from sqlalchemy.orm import relationship
import enum

class ActivityComments(Base):
    __tablename__ = "Activity Comments"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False)
    # Author info
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    headline = Column(String(300), nullable=True)
    username = Column(String(100), nullable=False, index=True)
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

    lower_limit = Column(Integer, nullable=True)
    upper_limit = Column(Integer, nullable=True)

    status = Column(Enum(JobStatusEnum), default=JobStatusEnum.pending)
    remark = Column(Text, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
