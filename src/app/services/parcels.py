import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.schemas.parcels import (
    ParcelCreate,
    ParcelOut,
    ParcelTypeRead,
)
from src.db.models.parcel import Parcel, ParcelType

from src.app.schemas.parcel import ParcelsListResponse


def generate_tracking_code() -> str:
    return uuid.uuid4().hex[:12].upper()


class ParcelService:
    async def get_parcel_types(
        self,
        db: AsyncSession,
    ) -> List[ParcelTypeRead]:
        result = await db.execute(select(ParcelType))
        types = result.scalars().all()
        return [ParcelTypeRead.model_validate(obj) for obj in types]

    async def create_parcel(
        self,
        db: AsyncSession,
        session_id: str,
        data: ParcelCreate,
    ) -> ParcelOut:
        tracking_code = generate_tracking_code()

        parcel = Parcel(
            session_id=session_id,
            name=data.name,
            weight=data.weight,
            parcel_type_id=data.parcel_type_id,
            declared_value_usd=data.declared_value_usd,
            delivery_cost_rub=None,
            tracking_code=tracking_code,
        )

        db.add(parcel)
        await db.commit()
        await db.refresh(parcel)

        return ParcelOut.model_validate(parcel)

    async def get_parcels(
        self,
        db: AsyncSession,
        session_id: str,
        parcel_type_id: Optional[int] = None,
        has_delivery_cost: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ParcelsListResponse:
        query = select(Parcel).where(Parcel.session_id == session_id)

        if parcel_type_id is not None:
            query = query.where(Parcel.parcel_type_id == parcel_type_id)

        if has_delivery_cost is True:
            query = query.where(Parcel.delivery_cost_rub.is_not(None))
        elif has_delivery_cost is False:
            query = query.where(Parcel.delivery_cost_rub.is_(None))

        total_result = await db.execute(
            query.with_only_columns(Parcel.id).order_by(None)
        )
        total = len(total_result.scalars().all())

        offset = (page - 1) * page_size
        query = query.order_by(Parcel.created_at.desc()).offset(offset).limit(page_size)

        result = await db.execute(query)
        parcels = result.scalars().all()

        items = [ParcelOut.model_validate(p) for p in parcels]

        return ParcelsListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )
