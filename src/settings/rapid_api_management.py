from pydantic_settings import BaseSettings

class RapidApiManagementSettings(BaseSettings):
    BASE_URL : str = "linkedin-data-api.p.rapidapi.com"
    BASE_URL_2 : str = "linkedin-bulk-data-scraper.p.rapidapi.com"
    class Config:
        env_prefix = "DB_"

# Create an instance that you can import elsewhere
rapid_api_management = RapidApiManagementSettings()