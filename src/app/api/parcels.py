from typing import List
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.schemas.parcels import (
    ParcelCreate,
    ParcelOut,
    ParcelTypeRead,
    ParcelsListResponse,
)
from src.app.db.sessions import get_db
from src.app.services.parcels import ParcelService

router = APIRouter(prefix="/parcels", tags=["parcels"])


@router.post(
    "",
    response_model=ParcelOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_parcel(
    request: Request,
    data: ParcelCreate,
    # db: AsyncSession = Depends(get_db),
    # service: ParcelService = Depends(),
):
    session_id = getattr(request.state, "session_id", None)
    if not session_id:
        raise HTTPException(status_code=401, detail="Нужно ввести айди сессии")
    raise HTTPException(status_code=501, detail="Заказ еще не создан")


@router.get(
    "/types",
    response_model=List[ParcelTypeRead],
)
async def get_parcel_types(
    # db: AsyncSession = Depends(get_db),
    # service: ParcelService = Depends(),
):
    raise HTTPException(status_code=501, detail="Заказ еще не создан")


@router.get(
    "",
    response_model=ParcelsListResponse,
)
async def list_parcels(
    request: Request,
    parcel_type_id: int | None = None,
    has_delivery_cost: bool | None = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    service: ParcelService = Depends(),
):
    session_id = getattr(request.state, "session_id", None)
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется сессия",
        )

    if page < 1 or page_size < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Некорректные параметры пагинации",
        )

    return await service.get_parcels(
        db=db,
        session_id=session_id,
        parcel_type_id=parcel_type_id,
        has_delivery_cost=has_delivery_cost,
        page=page,
        page_size=page_size,
    )
