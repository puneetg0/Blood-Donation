from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 60
    algorithm: str = "HS256"
    cors_origins: str = "http://localhost:5173,http://localhost:5174"

    #This tells pydantic- settings to read a file named .env
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
