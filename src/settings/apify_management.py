from pydantic_settings import BaseSettings

class ApifyManagementSettings(BaseSettings):
    NUMBER_OF_POSTS : int = 35
    MINIMUM_DEPLY : int = 2
    MAXIMUM_DELAY : int = 8
    class Config:
        env_prefix = "DB_"

# Create an instance that you can import elsewhere
apify_management = ApifyManagementSettings()