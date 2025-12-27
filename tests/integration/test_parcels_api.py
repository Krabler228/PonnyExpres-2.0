from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from src.app.db.models.parcel import Parcel, ParcelType


@pytest.mark.asyncio
async def test_create_parcel_success(client: AsyncClient, db_session):
    pt = ParcelType(name="box-success")
    db_session.add(pt)
    await db_session.commit()
    await db_session.refresh(pt)

    payload = {
        "name": "Test Parcel",
        "weight": "1.234",
        "parcel_type_id": pt.id,
        "declared_value_usd": "100.00",
    }

    response = await client.post(
        "/parcels",
        json=payload,
        cookies={"session_id": "session-123"},
    )
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == payload["name"]
    assert data["parcel_type_id"] == pt.id
    assert "id" in data

    result = await db_session.execute(select(Parcel).where(Parcel.id == data["id"]))
    db_parcel = result.scalar_one()

    assert db_parcel.name == payload["name"]
    assert db_parcel.parcel_type_id == pt.id
    assert db_parcel.weight == Decimal(payload["weight"])


@pytest.mark.asyncio
async def test_create_parcel_invalid_payload_returns_422(
    client: AsyncClient,
    db_session,
):
    pt = ParcelType(name="box-invalid")
    db_session.add(pt)
    await db_session.commit()
    await db_session.refresh(pt)

    payload = {
        "name": "Bad parcel",
        # weight отсутствует
        "parcel_type_id": pt.id,
        "declared_value_usd": "100.00",
    }

    response = await client.post(
        "/parcels",
        json=payload,
        cookies={"session_id": "session-xyz"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_parcels_returns_created(client: AsyncClient, db_session):
    pt = ParcelType(name="envelope-list")
    db_session.add(pt)
    await db_session.commit()
    await db_session.refresh(pt)

    parcel = Parcel(
        session_id="session-456",
        name="List parcel",
        weight=Decimal("0.500"),
        parcel_type_id=pt.id,
        declared_value_usd=Decimal("50.00"),
        delivery_cost_rub=Decimal("300.00"),
        tracking_code="LIST-123",
    )
    db_session.add(parcel)
    await db_session.commit()

    response = await client.get(
        "/parcels",
        params={"page": 1, "page_size": 10},
        cookies={"session_id": "session-456"},
    )
    assert response.status_code == 200

    data = response.json()
    items = data["items"]
    assert any(p["id"] == parcel.id for p in items)
