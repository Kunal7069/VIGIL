from pydantic_settings import BaseSettings

class PriceManagementSettings(BaseSettings):
    POSTS_CREDIT : int = 1
    POSTS_BATCH: int = 50
    PROFILE_CREDIT : int = 1
    ACTIVITY_COMMENTS_CREDIT : int = 1
    ACTIVITY_REACTIONS_CREDIT : int = 1
    ACTIVITY_REACTIONS_BATCH : int = 100
    COMMENTORS_CREDIT : int = 1
    URN_TO_URL_CREDIT : int =1
    POST_URL_REACTORS_CREDIT_1 :int = 2
    POST_URL_REACTORS_CREDIT_2 :int = 1
    WITHOUT_POST_URL_REACTORS_CREDIT_1 :int = 3
    WITHOUT_POST_URL_REACTORS_CREDIT_2 :int = 2
    REACTORS_BATCH : int = 50
    
    class Config:
        env_prefix = "DB_"
        env_file = ".env"

# Create an instance that you can import elsewhere
price_management = PriceManagementSettings()