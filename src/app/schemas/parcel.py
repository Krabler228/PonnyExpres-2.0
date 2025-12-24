from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class ParcelTypeBase(BaseModel):
    name: str


class ParcelTypeCreate(ParcelTypeBase):
    pass


class ParcelTypeRead(ParcelTypeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ParcelBase(BaseModel):
    name: str
    weight: Decimal
    parcel_type_id: int
    declared_value_usd: Decimal
    delivery_cost_rub: Decimal | None = None


class ParcelCreate(BaseModel):
    name: str
    weight: Decimal
    parcel_type_id: int
    declared_value_usd: Decimal


class ParcelOut(ParcelBase):
    id: int
    session_id: str
    tracking_code: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PublicParcelOut(BaseModel):
    id: int
    name: str
    weight: Decimal
    parcel_type_id: int
    declared_value_usd: Decimal
    delivery_cost_rub: Optional[str] = None
    tracking_code: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ParcelsListResponse(BaseModel):
    items: List[ParcelOut]
    total: int
    page: int
    page_size: int
