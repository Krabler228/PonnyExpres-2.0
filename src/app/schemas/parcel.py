from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ParcelTypeBase(BaseModel):
    name: str


class ParcelTypeCreate(ParcelTypeBase):
    pass


class ParcelTypeRead(ParcelTypeBase):
    id: int

    model_config = ConfigDict(from_atributes=True)


class ParcelBase(BaseModel):
    session_id: str
    name: str
    weight: Decimal
    parcel_type_id: int
    declared_value_usd: Decimal
    delivery_cost_rub: Decimal | None = None


class ParcelCreate(ParcelBase):
    pass


class ParcelRead(ParcelBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
