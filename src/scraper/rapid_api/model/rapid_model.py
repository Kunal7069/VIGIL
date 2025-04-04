from pydantic import BaseModel, Field, model_validator

class ActivityRequest(BaseModel):
    type : str
    username: str
    activity_comments: str = Field(..., pattern="^(yes|no)$")
    activity_reactions: str = Field(..., pattern="^(yes|no)$")
    profile_info: str = Field(..., pattern="^(yes|no)$")
    post_scrap: str = Field(..., pattern="^(yes|no)$")
    post_comments: str = Field(..., pattern="^(yes|no)$")
    post_reactions: str = Field(..., pattern="^(yes|no)$")
    post_limit: int | None = None
    comment_limit: int | None = None
    reaction_limit: int | None = None
    
    

    @model_validator(mode="after")
    def validate_post_scrap(self) -> "ActivityRequest":
        if self.post_scrap == "yes" and self.post_limit is None:
            raise ValueError("lower_limit and upper_limit are required when post_scrap is 'yes'")
        return self
    
class SearchPostsRequest(BaseModel):
    keyword: str
    num_posts: int