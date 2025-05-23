from dotenv import load_dotenv
import os

load_dotenv() 

secret_key = os.getenv("SECRET_KEY")
algorithm = os.getenv("ALGORITHM")
expire_minutes = int(os.getenv("EXPIRE", 120))
mongo_url = os.getenv("DATABASE_URL")


modules = [
    "users",
]