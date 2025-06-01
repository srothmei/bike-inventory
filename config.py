import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file if it exists
env_path = Path('.env')
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# Application configuration
class Config:
    """Configuration variables for the application"""
    # Database settings
    DB_PATH = os.getenv('DB_PATH', 'bike_inventory.db')
    
    # Storage settings
    STATIC_DIR = Path(__file__).parent / "static"
    IMAGE_DIR = STATIC_DIR / "images"
    
    # Environment
    DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')
    
    # Ensure directories exist
    @classmethod
    def init_dirs(cls):
        cls.STATIC_DIR.mkdir(exist_ok=True)
        cls.IMAGE_DIR.mkdir(exist_ok=True)
        
    # Get the list of categories
    @classmethod
    def get_categories(cls):
        return ["Frame", "Wheels", "Drivetrain", "Brakes", "Controls", "Other"]
