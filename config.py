import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8180960426:AAFmpswRZKJqikqiubD8V45AQGfOFGi5tJk')

# OpenAI API Key
OPENAI_API_KEY = os.getenv('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')

# Database
DATABASE_PATH = 'outfitify.db'

# Bot settings
MAX_PHOTO_SIZE = 10 * 1024 * 1024  # 10MB
SUPPORTED_PHOTO_FORMATS = ['jpg', 'jpeg', 'png', 'webp'] 