import os

class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/portaai_db"
    )

    SECRET_KEY: str = "supersecretkey"
    ALGORITHM: str = "HS256"

settings = Settings()