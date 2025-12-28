from decimal import Decimal
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker


from src.app.db.base import Base
from src.app.db.models.parcel import Parcel, ParcelType
from src.app.tasks.recalculate_delivery import recalculate_delivery_costs, UsdRateCache

TEST_SYNC_DB_URL = "sqlite:///:memory:"


@pytest.fixture
def sync_engine():
    engine = create_engine(
        TEST_SYNC_DB_URL,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def sync_session(sync_engine):
    SessionLocal = sessionmaker(bind=sync_engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


def test_recalculate_delivery_costs_updates_parcels(sync_session, monkeypatch):
    def fake_get_sync_session():
        return sync_session

    monkeypatch.setattr(
        "src.app.tasks.recalculate_delivery.get_sync_session",
        fake_get_sync_session,
    )

    parcel_type = ParcelType(id=1, name="test_type")
    sync_session.add(parcel_type)
    sync_session.commit()

    with patch.object(UsdRateCache, "get_rate", return_value=90.0):
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
        assert len(refreshed) == 2
