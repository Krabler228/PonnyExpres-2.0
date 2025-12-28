from pymongo import MongoClient
from pydantic import BaseModel


class DeliveryLog(BaseModel):
    parcel_id: int
    timestamp: str
    weight_kg: float
    declared_value_usd: float
    usd_rate: float
    delivery_cost_rub: float
    parcel_type_id: int


class MongoDeliveryLogger:
    def __init__(self):
        self.sync_client = None
        self.db = None

    def connect_sync(self):
        self.sync_client = MongoClient(
            "mongodb://root:root@mongodb:27017", serverSelectionTimeoutMS=5000
        )
        self.db = self.sync_client["ponnyexpres"]

    def log_delivery_calculation(self, log: DeliveryLog):
        if self.db:
            self.db.delivery_logs.insert_one(log.dict())

    def close(self):
        if self.sync_client:
            self.sync_client.close()


mongo_logger = MongoDeliveryLogger()
