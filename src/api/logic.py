# ==================================================================================================
#   `api` business logic
# ==================================================================================================

import httpx
from dataclasses import dataclass
from json.decoder import JSONDecodeError

from django.conf import settings

from .models import Currency
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
#   Business logic
# --------------------------------------------------------------------------------------------------
@dataclass
class ExchangeApi:
    """External exchange API access entity."""

    url: str = settings.EXCHANGE_RATES_API_URL
    timeout: int = settings.EXCHANGE_RATES_API_TIMEOUT

    def __post_init__(self):
        self.exchange_rates = {}
        self.last_update = None

    def _process_data(self, data) -> None:
        """Process and validate API data."""
        self.last_update = data.get('lastupdate')
        self.last_update_iso = self.last_update.isoformat()

        self.exchange_rates = {
            currency_name: float(exchange_rate)
            for currency_name, exchange_rate in data.get('rates').items()
            if currency_name in Currency.cached_acronyms_list()
        }

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

        exchange_serializer = ExchangeApiInputSerializer(data=result_data)
        if not exchange_serializer.is_valid():
            return OutputStatus(
                status='invalid_api_data_error',
                error=True,
                data={'error': {'Invalid API response': exchange_serializer.errors}},
            )

        self._process_data(data=exchange_serializer.validated_data)

        return OutputStatus(
            status='ok',
            error=False,
            data={'exchange_rates': self.exchange_rates, 'updated': self.last_update_iso},
        )
