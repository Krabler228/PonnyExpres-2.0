import logging
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.app.tasks.celery_app import celery_app
from src.app.cache.rates import UsdRateCache
from src.app.db.session_sync import get_sync_session
from src.app.db.models.parcel import Parcel

logger = logging.getLogger(__name__)


@celery_app.task(
    name="src.app.tasks.recalculate_delivery.recalculate_delivery_costs",
    bind=True,
    max_retries=3,
    default_retry_delay=5,
)
def recalculate_delivery_costs(self):
    logger.info("Считаю стоимость доставки...")

    try:
        usd_rate = UsdRateCache().get_rate()
    except Exception as exc:
        logger.error(f"Ошибка получения курса USD/RUB: {exc}")
        raise self.retry(exc=exc)
    session: Session = get_sync_session()
    updated_count = 0

    try:
        stmt = select(Parcel).where(Parcel.delivery_cost_rub.is_(None))
        parcels = session.execute(stmt).scalars().all()

        if not parcels:
            logger.info("Нет посылок для пересчёта стоимости доставки")
            return
        logger.info(f"Найдено {len(parcels)} посылок для пересчёта")

        for parcel in parcels:
            weight = Decimal(parcel.weight)
            declared_value_usd = Decimal(parcel.declared_value_usd)

            cost_rub = (
                weight * Decimal("0.5") + declared_value_usd * Decimal("0.01")
            ) * Decimal(str(usd_rate))

            parcel.delivery_cost_rub = cost_rub.quantize(Decimal("0.01"))
            updated_count += 1

        session.commit()
        logger.info(f"Пересчёт стоимости завершён, обновлено посылок: {updated_count}")

    except Exception as exc:
        session.rollback()
        logger.error(f"Ошибка при пересчёте стоимости доставки: {exc}")

        raise
    finally:
        session.close()
