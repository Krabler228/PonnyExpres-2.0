import pytest
from decimal import Decimal
from unittest.mock import patch
from sqlalchemy import select

from src.app.tasks.recalculate_delivery import recalculate_delivery_costs, UsdRateCache
from src.app.db.models.parcel import Parcel, ParcelType


@pytest.mark.unit
def test_recalculate_delivery_unit(sqlite_session):
    parcel_type = ParcelType(id=1, name="unit_test")
    sqlite_session.add(parcel_type)
    sqlite_session.commit()

    parcel = Parcel(
        session_id="unit_session",
        name="Unit Test Parcel",
        weight=Decimal("1.000"),
        parcel_type_id=1,
        declared_value_usd=Decimal("100.00"),
        delivery_cost_rub=None,
        tracking_code="UNIT123",
    )
    sqlite_session.add(parcel)
    sqlite_session.commit()

    def fake_get_sync_session():
        return sqlite_session

    with (
        patch(
            "src.app.tasks.recalculate_delivery.get_sync_session", fake_get_sync_session
        ),
        patch.object(UsdRateCache, "get_rate", return_value=90.0),
    ):
        recalculate_delivery_costs()

    refreshed = sqlite_session.execute(
        select(Parcel).where(Parcel.tracking_code == "UNIT123")
    ).scalar_one()

    assert refreshed.delivery_cost_rub is not None
    assert refreshed.delivery_cost_rub > 0
    assert len(refreshed.__dict__) > 0
