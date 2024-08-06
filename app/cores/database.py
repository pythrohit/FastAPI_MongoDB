from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pymongo.errors import ServerSelectionTimeoutError
from app.cores.config import settings


class MongoDBManager:
    def __init__(self, uri: str, db_name: str):
        self.uri = uri
        self.db_name = db_name
        self.client = None
        self.db = None

    async def connect(self):
        try:
            self.client = AsyncIOMotorClient(self.uri)
            self.db = self.client[self.db_name]
            await self.db['users'].create_index('email', unique=True)
            print("MongoDB Connected..")
        except ServerSelectionTimeoutError:
            print("MongoDB connection Timeout error:Unable to connect mongoDB")
        except Exception:
            print("An error occurred while connecting to MongoDB")

    async def disconnect(self):
        if self.client:
            self.client.close()
            print("MongoDB Disconnected..")

    def __getattr__(self, name):
        return self.db[name]


db = MongoDBManager(uri=settings.DATABASE_URL, db_name=settings.DATABASE_NAME)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    print("Request handling start")
    yield
    print("Request handling stop")
    await db.disconnect()
