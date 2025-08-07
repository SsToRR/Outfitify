import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', 'Your telegram bot token')

# OpenAI API Key
OPENAI_API_KEY = os.getenv('Your Open AI key')

# Database
DATABASE_PATH = 'outfitify.db'

# Bot settings
MAX_PHOTO_SIZE = 10 * 1024 * 1024  # 10MB
SUPPORTED_PHOTO_FORMATS = ['jpg', 'jpeg', 'png', 'webp'] 
