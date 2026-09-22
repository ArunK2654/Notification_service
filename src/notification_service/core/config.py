from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str
    database_url: str

    smtp_email: str
    smtp_app_password: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    redis_url: str

    model_config = {"extra": "ignore", "env_file": ".env.dev"}


settings = Settings()
