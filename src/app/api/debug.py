from fastapi import APIRouter, status

from src.app.tasks.recalculate_delivery import recalculate_delivery_costs

router = APIRouter(prefix="/debug", tags=["debug"])


@router.post(
    "/recalculate_delivery",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Ручной запуск пересчёта стоимости доставки",
)
async def trigger_recalculate_delivery() -> dict:
    task = recalculate_delivery_costs.delay()
    return {"task_id": task.id}
