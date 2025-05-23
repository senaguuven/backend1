from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine
from config import settings

# Motor client ile bağlantı oluştur
client = AsyncIOMotorClient(settings.mongo_url)


# Odmantic engine
db = AIOEngine(client=client, database="kankanX")