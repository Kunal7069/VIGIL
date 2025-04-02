from pydantic_settings import BaseSettings

class DatabaseManagementSettings(BaseSettings):
    DATABASE_URL : str = "postgresql://neondb_owner:npg_OSU2fNHX6Gsn@ep-tight-paper-a5pfl68c-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
    rapid_api_key: str = "60f96f2c9bmshb9a09ca8342a8ccp12b2a2jsn71c56525a1c8"
    class Config:
        env_prefix = "DB_"
        env_file = ".env"

# Create an instance that you can import elsewhere
database_management = DatabaseManagementSettings()