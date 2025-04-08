from pydantic_settings import BaseSettings

class DatabaseManagementSettings(BaseSettings):
    DATABASE_URL : str = "postgresql://neondb_owner:npg_OSU2fNHX6Gsn@ep-tight-paper-a5pfl68c-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
    rapid_api_key: str = "e7fd4b5f0dmsh833f96f2d6e1636p13ea56jsn7b0cce305148"
    class Config:
        env_prefix = "DB_"
        env_file = ".env"

# Create an instance that you can import elsewhere
database_management = DatabaseManagementSettings()