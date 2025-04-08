from pydantic_settings import BaseSettings

class DatabaseManagementSettings(BaseSettings):
    DATABASE_URL : str = "postgresql://neondb_owner:npg_OSU2fNHX6Gsn@ep-tight-paper-a5pfl68c-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
    rapid_api_key: str = "d586e7b220msh4c0231f7ff21cd1p169bacjsn04caead9c266"
    class Config:
        env_prefix = "DB_"
        env_file = ".env"

# Create an instance that you can import elsewhere
database_management = DatabaseManagementSettings()