from decimal import Decimal
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine, select, Table, Column, Integer
from sqlalchemy.orm import sessionmaker

from src.app.db.base import Base
from src.app.db.models.parcel import Parcel
from src.app.tasks import recalculate_delivery
from src.app.tasks.recalculate_delivery import recalculate_delivery_costs

TEST_SYNC_DB_URL = "sqlite:///:memory:"


@pytest.fixture
def sync_session():
    engine = create_engine(TEST_SYNC_DB_URL)

    Table(
        "parcels",
        Base.metadata,
        Column("id", Integer, primary_key=True, autoincrement=True),
        extend_existing=True,
    )

    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def test_recalculate_delivery_costs_updates_parcels(sync_session, monkeypatch):
    def fake_get_sync_session():
        return sync_session

    monkeypatch.setattr(
        "src.app.tasks.recalculate_delivery.get_sync_session",
        fake_get_sync_session,
    )

    with patch.object(
        recalculate_delivery.UsdRateCache,
        "get_rate",
        return_value=90.0,
    ):
        parcel1 = Parcel(
            session_id="s1",
            name="P1",
            weight=Decimal("1.000"),
            parcel_type_id=1,
            declared_value_usd=Decimal("100.00"),
            delivery_cost_rub=None,
            tracking_code="T1",
        )
        parcel2 = Parcel(
            session_id="s2",
            name="P2",
            weight=Decimal("2.000"),
            parcel_type_id=1,
            declared_value_usd=Decimal("200.00"),
            delivery_cost_rub=None,
            tracking_code="T2",
        )
        sync_session.add_all([parcel1, parcel2])
        sync_session.commit()

        recalculate_delivery_costs()

        refreshed = (
            sync_session.execute(
                select(Parcel).where(Parcel.tracking_code.in_(["T1", "T2"]))
            )
            .scalars()
            .all()
        )

        assert all(p.delivery_cost_rub is not None for p in refreshed)
