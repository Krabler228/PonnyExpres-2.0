from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Optional

import redis
import requests

from src.app.core.config import settings

CBR_URL = "https://www.cbr-xml-daily.ru/daily_json.js"
USD_RATE_CACHE_KEY = "usd_rate"


@dataclass
class UsdRateCacheConfig:
    host: str
    port: int
    db: int
    ttl_seconds: int = 300  # 5 минут


class UsdRateCache:
    def __init__(self, config: Optional[UsdRateCacheConfig] = None) -> None:
        if config is None:
            config = UsdRateCacheConfig(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
            )

        self._config = config
        self._client = redis.Redis(
            host=config.host,
            port=config.port,
            db=config.db,
            decode_responses=True,  # получать строки, а не bytes
        )

    def get_rate(self) -> float:
        try:
            cached_value = self._client.get(USD_RATE_CACHE_KEY)
        except redis.RedisError:
            cached_value = None

        if cached_value is not None:
            try:
                return float(cached_value)
            except (TypeError, ValueError):
                # битое значение в кэше — игнорируем и перезапрашиваем
                pass

        rate = self._fetch_from_cbr()

        try:
            self._client.setex(
                USD_RATE_CACHE_KEY,
                self._config.ttl_seconds,
                str(rate),
            )
        except redis.RedisError:
            # падение Redis не должно ломать сервис
            pass

        return rate

    def _fetch_from_cbr(self) -> float:
        try:
            resp = requests.get(CBR_URL, timeout=5)
            resp.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(f"Не удалось получить курс USD из ЦБ РФ: {exc}") from exc

        try:
            data = resp.json()
        except json.JSONDecodeError as exc:
            raise RuntimeError("Не удалось разобрать ответ ЦБ РФ как JSON") from exc

        try:
            rate = float(data["Valute"]["USD"]["Value"])
        except (KeyError, TypeError, ValueError) as exc:
            raise RuntimeError(
                "Некорректная структура JSON ЦБ РФ для курса USD"
            ) from exc

        return rate
