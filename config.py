import os
from dotenv import load_dotenv

load_dotenv()

# LinkedIn API
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")

# OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Database
DATABASE_PATH = os.getenv("DATABASE_PATH", "linkedin_bot.db")

# Convex
CONVEX_URL = os.getenv("CONVEX_URL")
