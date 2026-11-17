import os
from datetime import timedelta

class Config:
    """Base configuration class containing application constants and settings."""

    SECRET_KEY: str = os.environ.get('SECRET_KEY', 'default-inseed-secret-key-for-local-dev')

    DB_FILE_PATH: str = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'inseed.sqlite')
    SQLALCHEMY_DATABASE_URI: str = f"sqlite:///{DB_FILE_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    JWT_SECRET_KEY: str = os.environ.get('JWT_SECRET_KEY', 'default-inseed-jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(hours=1)
    JWT_HEADER_NAME: str = 'Authorization'
    JWT_HEADER_TYPE: str = 'Bearer'

    DEBUG: bool = False
    TESTING: bool = False

class DevelopmentConfig(Config):
    """Development configuration setup."""
    DEBUG: bool = True

class ProductionConfig(Config):
    """Production configuration setup."""
    pass

class TestingConfig(Config):
    """Testing configuration setup."""
    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"

def get_config() -> type[Config]:
    """Returns the appropriate configuration class based on FLASK_ENV setting."""
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        return ProductionConfig
    if env == 'testing':
        return TestingConfig
    return DevelopmentConfig