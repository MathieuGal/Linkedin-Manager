import os
from dotenv import load_dotenv

load_dotenv()

# LinkedIn API
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")

# Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Database
DATABASE_PATH = os.getenv("DATABASE_PATH", "linkedin_bot.db")

# Convex
CONVEX_URL = os.getenv("CONVEX_URL")
