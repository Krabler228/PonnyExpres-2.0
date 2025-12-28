import logging
from decimal import Decimal
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.app.tasks.celery_app import celery_app
from src.app.cache.rates import UsdRateCache
from src.app.db.session_sync import get_sync_session
from src.app.db.models.parcel import Parcel
from src.app.logging.mongo_logger import mongo_logger, DeliveryLog

logger = logging.getLogger(__name__)


@celery_app.task(
    name="src.app.tasks.recalculate_delivery.recalculate_delivery_costs",
    bind=True,
    max_retries=3,
    default_retry_delay=5,
)
def recalculate_delivery_costs(self):
    logger.info("Celery recalculate_delivery_costs started")
    mongo_logger.connect_sync()

    try:
        usd_rate = UsdRateCache().get_rate()
        logger.info(f"USD rate fetched: {usd_rate}")
    except Exception as exc:
        logger.error(f"CBR rate fetch failed [error={exc}]")
        mongo_logger.close()
        raise self.retry(exc=exc)

    session: Session = get_sync_session()
    updated_count = 0

    try:
        stmt = select(Parcel).where(Parcel.delivery_cost_rub.is_(None))
        parcels = session.execute(stmt).scalars().all()

        if not parcels:
            logger.info("No parcels for recalculation")
            mongo_logger.close()
            return

        logger.info(
            f"Found {len(parcels)} parcels for recalculation [parcels_count={len(parcels)}]"
        )

        for parcel in parcels:
            weight = Decimal(parcel.weight)
            declared_value_usd = Decimal(parcel.declared_value_usd)

            cost_rub = (
                weight * Decimal("0.5") + declared_value_usd * Decimal("0.01")
            ) * Decimal(str(usd_rate))

            parcel.delivery_cost_rub = cost_rub.quantize(Decimal("0.01"))

            # MongoDB log с обработкой ошибок
            try:
                mongo_logger.log_delivery_calculation(
                    DeliveryLog(
                        parcel_id=parcel.id,
                        timestamp=datetime.now().isoformat(),
                        weight_kg=float(weight),
                        declared_value_usd=float(declared_value_usd),
                        usd_rate=float(usd_rate),
                        delivery_cost_rub=float(cost_rub),
                        parcel_type_id=parcel.parcel_type_id,
                    )
                )
                logger.info(f"MongoDB log saved for parcel {parcel.id}")
            except Exception as mongo_exc:
                logger.error(
                    f"MongoDB log failed for parcel {parcel.id} [error={mongo_exc}]"
                )

            updated_count += 1

        session.commit()
        logger.info(
            f"Updated {updated_count} parcels [usd_rate={usd_rate}, avg_cost={float(cost_rub):.2f}]"
        )

    except Exception as exc:
        session.rollback()
        logger.error(f"Delivery recalculation failed [error={exc}]")
        raise
    finally:
        session.close()
        mongo_logger.close()
