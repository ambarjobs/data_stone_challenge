# ==================================================================================================
#   `api` business logic
# ==================================================================================================

import httpx
from dataclasses import dataclass
from datetime import datetime
from json.decoder import JSONDecodeError

from django.conf import settings

from .serializers import ExchangeApiInputSerializer


# --------------------------------------------------------------------------------------------------
#   Output status
# --------------------------------------------------------------------------------------------------
@dataclass
class OutputStatus:
    """Business logic output status."""
    status: str
    error: bool
    data: dict


# --------------------------------------------------------------------------------------------------
#   Output status
# --------------------------------------------------------------------------------------------------
@dataclass
class ExchangeApi:
    """External exchange API access entity."""

    url: str = settings.EXCHANGE_RATES_API_URL
    timeout: int = settings.EXCHANGE_RATES_API_TIMEOUT

    def __post_init__(self):
        self.exchange_rates = {}
        self.last_update = None

    def get_exchange_rates(self) -> OutputStatus:
        """Get the exchange rates with the external API."""
        try:
            result = httpx.get(url=self.url, timeout=self.timeout)

            result.raise_for_status()
        except (httpx.HTTPStatusError, httpx.ConnectError) as err:
            return OutputStatus(status='api_access_error', error=True, data={'error': str(err)})

        try:
            result_data = result.json()
        except JSONDecodeError as err:
            return OutputStatus(
                status='json_data_error',
                error=True,
                data={'error': f'Invalid JSON: {err}'},
            )

        try:
            exchange_serializer = ExchangeApiInputSerializer(data=result_data)
            if not exchange_serializer.is_valid():
                raise ValueError

            last_update_iso = result_data.get('lastupdate')
            self.last_update = datetime.fromisoformat(last_update_iso)

            self.exchange_rates = {
                currency_name: float(exchange_rate)
                for currency_name, exchange_rate in result_data.get('rates').items()
                if currency_name in settings.CURRENCY_LIST
            }
        except (TypeError, ValueError) as err:
            return OutputStatus(
                status='invalid_api_data_error',
                error=True,
                data={'error': f'Invalid API response: {err}'},
            )

        return OutputStatus(
            status='ok',
            error=False,
            data={'exchange_rates': self.exchange_rates, 'updated': last_update_iso},
        )
