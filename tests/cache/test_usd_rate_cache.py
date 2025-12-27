import json
from unittest.mock import patch

import fakeredis
import pytest
import requests

from src.app.cache.rates import (
    UsdRateCache,
    UsdRateCacheConfig,
    USD_RATE_CACHE_KEY,
)


@pytest.fixture
def fake_redis_client():
    client = fakeredis.FakeRedis(decode_responses=True)
    return client


@pytest.fixture
def usd_rate_cache(fake_redis_client):
    config = UsdRateCacheConfig(host="localhost", port=6379, db=0, ttl_seconds=300)
    cache = UsdRateCache(config=config)
    cache._client = fake_redis_client
    return cache


def test_get_rate_returns_cached_value(usd_rate_cache, fake_redis_client):
    fake_redis_client.set(USD_RATE_CACHE_KEY, "92.34")

    with patch.object(usd_rate_cache, "_fetch_from_cbr") as mock_fetch:
        rate = usd_rate_cache.get_rate()

    assert rate == pytest.approx(92.34)
    mock_fetch.assert_not_called()


def test_get_rate_fetches_from_cbr_and_caches(usd_rate_cache, fake_redis_client):
    with patch("src.app.cache.rates.requests.get") as mock_get:
        mock_resp = requests.Response()
        mock_resp.status_code = 200
        payload = {
            "Valute": {
                "USD": {
                    "Value": 93.21,
                }
            }
        }
        mock_resp._content = json.dumps(payload).encode("utf-8")
        mock_get.return_value = mock_resp

        rate = usd_rate_cache.get_rate()

    assert rate == pytest.approx(93.21)

    cached = fake_redis_client.get(USD_RATE_CACHE_KEY)
    assert float(cached) == pytest.approx(93.21)


def test_get_rate_ignores_broken_cached_value(usd_rate_cache, fake_redis_client):
    fake_redis_client.set(USD_RATE_CACHE_KEY, "not-a-number")

    with patch("src.app.cache.rates.requests.get") as mock_get:
        mock_resp = requests.Response()
        mock_resp.status_code = 200
        payload = {
            "Valute": {
                "USD": {
                    "Value": 95.0,
                }
            }
        }
        mock_resp._content = json.dumps(payload).encode("utf-8")
        mock_get.return_value = mock_resp

        rate = usd_rate_cache.get_rate()

    assert rate == pytest.approx(95.0)


@pytest.fixture
def usd_rate_cache_no_redis():
    config = UsdRateCacheConfig(host="localhost", port=6379, db=0, ttl_seconds=300)
    return UsdRateCache(config=config)


def test_fetch_from_cbr_network_error(usd_rate_cache_no_redis, monkeypatch):
    def fake_get(url, timeout):
        raise requests.RequestException("boom")

    monkeypatch.setattr("src.app.cache.rates.requests.get", fake_get)

    with pytest.raises(RuntimeError):
        usd_rate_cache_no_redis._fetch_from_cbr()


def test_fetch_from_cbr_bad_json(usd_rate_cache_no_redis, monkeypatch):
    class FakeResp:
        status_code = 200

        def raise_for_status(self):
            return None

        def json(self):
            raise json.JSONDecodeError("err", "doc", 0)

    monkeypatch.setattr(
        "src.app.cache.rates.requests.get", lambda url, timeout: FakeResp()
    )

    with pytest.raises(RuntimeError):
        usd_rate_cache_no_redis._fetch_from_cbr()


def test_fetch_from_cbr_invalid_structure(usd_rate_cache_no_redis, monkeypatch):
    class FakeResp:
        status_code = 200

        def raise_for_status(self):
            return None

        def json(self):
            return {"Valute": {}}

    monkeypatch.setattr(
        "src.app.cache.rates.requests.get", lambda url, timeout: FakeResp()
    )

    with pytest.raises(RuntimeError):
        usd_rate_cache_no_redis._fetch_from_cbr()
