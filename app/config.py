from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    africatalking_sms_username: str
    africatalking_sms_api_key: str
    google_client_id: str
    google_client_secret: str
    session_secret_key: str
    frontend_url: str
    jwt_secret_key: str
    jwt_algorithm: str
    jwt_access_token_expire_minutes: int

    class Config:
        env_file = ".env"


settings = Settings()
