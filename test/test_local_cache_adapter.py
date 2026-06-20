import asyncio

from src.infra.cache.local_cache_adapter import LocalCacheAdapter


def test_set_returns_success_and_persists_value():
    cache = LocalCacheAdapter()

    result = asyncio.run(cache.set('key', {'value': 1}, ex=60))
    stored = asyncio.run(cache.get('key'))

    assert result is True
    assert stored == {'value': 1}


def test_set_rejects_none_key():
    cache = LocalCacheAdapter()

    result = asyncio.run(cache.set(None, 'value'))

    assert result is False
