from pydantic_settings import BaseSettings

class DatabaseManagementSettings(BaseSettings):
    DATABASE_URL : str = "postgresql://neondb_owner:npg_OSU2fNHX6Gsn@ep-tight-paper-a5pfl68c-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
    rapid_api_key: str = "f11d18e7d2mshe024fef8bebbd54p14e5c7jsn25f976d93fe1"
    class Config:
        env_prefix = "DB_"
        env_file = ".env"

# Create an instance that you can import elsewhere
database_management = DatabaseManagementSettings()