from datetime import datetime
from json.decoder import JSONDecodeError

import httpx
import rest_framework.status as status
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
import json

# Just temporary.
CURRENCY_LIST = [
    'USD',
    'BRL',
    'EUR',
    'BTC',
    'ETH',
]

class Conversion(APIView):
    """Conversion resource."""

    def get(self, request):
        """Get currency conversion."""
        result = httpx.get(url=settings.EXCHANGE_RATES_API_URL)
        result.raise_for_status()

        try:
            result_data = result.json()
        except JSONDecodeError as err:
            return Response(
                data={'error': f'Invalid JSON: {err}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            last_update_iso = result_data.get('lastupdate')
            last_update = datetime.fromisoformat(last_update_iso)

            exchange_rates = {
                currency_name: float(exchange_rate)
                for currency_name, exchange_rate in result_data.get('rates').items()
                if currency_name in CURRENCY_LIST
            }
        except (TypeError, ValueError) as err:
            return Response(
                data={'error': f'Invalid API response: {err}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(data={'exchange_rates': exchange_rates, 'updated': last_update_iso})
