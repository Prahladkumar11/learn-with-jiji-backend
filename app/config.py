from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str
    # supabase_service_key: str
    jwt_secret: str
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
