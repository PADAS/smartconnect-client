import warnings

import pytest

from smartconnect import SmartClient, AsyncSmartClient, smart_settings


def test_sync_client_uses_custom_timeouts():
    client = SmartClient(
        api="https://test.example.com",
        username="u",
        password="p",
        read_timeout=42.0,
        connect_timeout=7.5,
    )
    timeout = client._session.timeout
    assert timeout.read == 42.0
    assert timeout.connect == 7.5
    assert timeout.pool == 7.5


def test_sync_client_falls_back_to_smart_settings():
    client = SmartClient(
        api="https://test.example.com",
        username="u",
        password="p",
    )
    timeout = client._session.timeout
    assert timeout.read == smart_settings.SMART_DEFAULT_TIMEOUT
    assert timeout.connect == smart_settings.SMART_DEFAULT_CONNECT_TIMEOUT


def test_async_client_uses_custom_timeouts():
    client = AsyncSmartClient(
        api="https://test.example.com",
        username="u",
        password="p",
        read_timeout=42.0,
        connect_timeout=7.5,
    )
    timeout = client._session.timeout
    assert timeout.read == 42.0
    assert timeout.connect == 7.5
    assert timeout.pool == 7.5


def test_async_client_falls_back_to_smart_settings():
    client = AsyncSmartClient(
        api="https://test.example.com",
        username="u",
        password="p",
    )
    timeout = client._session.timeout
    assert timeout.read == smart_settings.SMART_DEFAULT_TIMEOUT
    assert timeout.connect == smart_settings.SMART_DEFAULT_CONNECT_TIMEOUT


def test_async_client_data_timeout_alias_is_honored():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        client = AsyncSmartClient(
            api="https://test.example.com",
            username="u",
            password="p",
            data_timeout=99.0,
        )
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
    assert client._session.timeout.read == 99.0
    assert any("data_timeout" in str(w.message) for w in deprecations)


def test_async_client_read_timeout_wins_over_data_timeout():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        client = AsyncSmartClient(
            api="https://test.example.com",
            username="u",
            password="p",
            read_timeout=11.0,
            data_timeout=99.0,
        )
    assert client._session.timeout.read == 11.0
