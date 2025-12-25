from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db.session import get_db
from src.app.schemas.parcel import PublicParcelOut
from src.app.services.parcels import ParcelService

router = APIRouter(prefix="/public", tags=["public"])


@router.get(
    "/parcels/{tracking_code}",
    response_model=PublicParcelOut,
)
async def get_public_parcel(
    tracking_code: str,
    db: AsyncSession = Depends(get_db),
    service: ParcelService = Depends(),
):
    parcel = await service.get_public_by_tracking_code(
        db=db,
        tracking_code=tracking_code,
    )
    return parcel
