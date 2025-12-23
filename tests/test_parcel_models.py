from decimal import Decimal

from sqlalchemy import select, delete

from app.db.models.parcel import Parcel, ParcelType


def test_create_parcel(db_session):
    db_session.execute(delete(Parcel))
    db_session.execute(delete(ParcelType))
    db_session.commit()

    pt = ParcelType(name="test-type")
    db_session.add(pt)
    db_session.flush()

    parcel = Parcel(
        session_id="session-123",
        name="Test Parcel",
        weight=Decimal("1.234"),
        parcel_type_id=pt.id,
        declared_value_usd=Decimal("100.00"),
        delivery_cost_rub=Decimal("500.00"),
    )
    db_session.add(parcel)
    db_session.commit()

    db_parcel = db_session.execute(
        select(Parcel).where(Parcel.session_id == "session-123")
    ).scalar_one()

    assert db_parcel.name == "Test Parcel"
    assert db_parcel.parcel_type_id == pt.id
