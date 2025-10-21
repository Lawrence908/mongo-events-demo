import os
from typing import Literal

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration with database switching capability"""
    
    # Flask configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    
    # Database configuration
    DB_TYPE: Literal["local", "cloud"] = os.getenv("DB_TYPE", "local")
    
    # Local MongoDB (school network via SSH)
    LOCAL_MONGODB_URI = os.getenv("LOCAL_MONGODB_URI", "mongodb://localhost:27017/")
    LOCAL_DB_NAME = os.getenv("LOCAL_PRACTICE_DB_NAME", "EventSphere")
    
    # Cloud MongoDB Atlas
    CLOUD_MONGODB_URI = os.getenv("MONGODB_URI", "")
    CLOUD_DB_NAME = os.getenv("MONGODB_DB_NAME", "EventSphere")
    
    # Default database selection
    MONGODB_URI = LOCAL_MONGODB_URI if DB_TYPE == "local" else CLOUD_MONGODB_URI
    DB_NAME = LOCAL_PRACTICE_DB_NAME if DB_TYPE == "local" else CLOUD_DB_NAME
    
    # Application settings
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 5000))
    
    # Google Maps API configuration
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
    GOOGLE_MAPS_GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"
    GOOGLE_MAPS_DIRECTIONS_URL = "https://www.google.com/maps/dir/?api=1"
    
    @classmethod
    def get_connection_string(cls) -> tuple[str, str]:
        """Get current database connection string and name"""
        return cls.MONGODB_URI, cls.DB_NAME
    
    @classmethod
    def switch_database(cls, db_type: Literal["local", "cloud"]) -> None:
        """Switch database type at runtime"""
        cls.DB_TYPE = db_type
        if db_type == "local":
            cls.MONGODB_URI = cls.LOCAL_MONGODB_URI
            cls.DB_NAME = cls.LOCAL_DB_NAME
        else:
            cls.MONGODB_URI = cls.CLOUD_MONGODB_URI
            cls.DB_NAME = cls.CLOUD_DB_NAME

    # API Limits
    MAX_EVENTS_LIMIT = int(os.getenv("MAX_EVENTS_LIMIT", "100000"))  # Maximum number of events that can be returned in a single query
