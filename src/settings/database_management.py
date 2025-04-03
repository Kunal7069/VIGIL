from pydantic_settings import BaseSettings

class DatabaseManagementSettings(BaseSettings):
    DATABASE_URL : str = "postgresql://neondb_owner:npg_OSU2fNHX6Gsn@ep-tight-paper-a5pfl68c-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
    rapid_api_key: str = "1fd05cef4emshdf26ea1f45beb0fp11ee8cjsn35bbdbc1f1e2"
    class Config:
        env_prefix = "DB_"
        env_file = ".env"

# Create an instance that you can import elsewhere
database_management = DatabaseManagementSettings()