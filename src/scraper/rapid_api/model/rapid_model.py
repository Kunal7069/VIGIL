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
    lower_limit: int | None = None
    upper_limit: int | None = None
    

    @model_validator(mode="after")
    def validate_post_scrap(self) -> "ActivityRequest":
        if self.post_scrap == "yes" and self.lower_limit and self.upper_limit is None:
            raise ValueError("lower_limit and upper_limit are required when post_scrap is 'yes'")
        return self