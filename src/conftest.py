# ==================================================================================================
#   Pytest fixtures
# ==================================================================================================
from typing import Any

import httpx
import pytest
from django.conf import settings

@pytest.fixture
def currency_list() -> list[str]:
    """List of app available currencies."""
    return settings.CURRENCY_LIST

@pytest.fixture
def httpx_get_request() -> httpx.Request:
    """Mocked httpx GET request."""
    return httpx.Request(url='', method='GET')

@pytest.fixture
def exchange_api_result() -> dict[str, Any]:
    """Result from external exchange rate API."""
    return {
        'table': 'latest',
        'rates': {
            'AUD': 1.534728,
            'BRL': 5.013266,
            'BTC': 0.000014135743,
            'ETH': 0.0002806474,
            'EUR': 0.926861,
            'USD': 1,
        },
        'lastupdate': '2024-03-28T21:19:45.133000+00:00'
    }

@pytest.fixture
def expected_rates(exchange_api_result: dict[str, Any], currency_list: list[str]) -> dict[str, Any]:
    """Result from external exchange rate API including only the ones in currency list."""
    return {
        currency: rate for currency, rate in exchange_api_result['rates'].items() # type: ignore[attr-defined]
        if currency in currency_list
    }
