from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://pims:pims_dev@localhost:5432/pims_optimizer"
    cors_origins: list[str] = ["http://localhost:3000"]
    seed_demo_data: bool = True
    environment: str = "production"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @model_validator(mode="after")
    def normalize_database_url(self):
        """Render provides postgres:// URLs. SQLAlchemy needs postgresql+psycopg2://."""
        url = self.database_url
        if url.startswith("postgres://"):
            self.database_url = url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif url.startswith("postgresql://") and "+psycopg2" not in url:
            self.database_url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return self


settings = Settings()
