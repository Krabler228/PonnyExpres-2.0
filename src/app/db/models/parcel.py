from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ParcelType(Base):
    __tablename__ = "parcel_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[String] = mapped_column(String(100), unique=True, nullable=False)


class Parcel(Base):
    __tablename__ = "parcels"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    session_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(225), nullable=False)
    weight: Mapped[float] = mapped_column(Numeric(10, 3), nullable=False)
    parcel_type_id: Mapped[int] = mapped_column(
        ForeignKey("parcel_types.id"),
        nullable=False,
        index=True,
    )
    declared_value_usd: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    delivery_cost_rub: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )
    parcel_type: Mapped[ParcelType] = relationship()
