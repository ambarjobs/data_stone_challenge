import rest_framework.status as status
from django.conf import settings
from django.core.cache import caches
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.response import Response
from rest_framework.views import APIView

from .logic import ExchangeApi


class Conversion(APIView):
    """Conversion resource."""

    @method_decorator(
        cache_page(timeout=settings.EXCHANGE_RATES_CACHE_TIMEOUT, key_prefix='api_conversion_get')
    )
    def get(self, request):
        """Get currency conversion."""
        required_parameters = ['from', 'to', 'amount']
        if not all([param in request.query_params for param in required_parameters]):
            return Response(
                data={'error': 'There are missing parameters on query string.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        exchange_api = ExchangeApi()
        exchange_rates_status = exchange_api.get_exchange_rates()

        if exchange_rates_status.error:
            return Response(data=exchange_rates_status.data, status=status.HTTP_400_BAD_REQUEST)

        exchange_rates = exchange_rates_status.data.get('exchange_rates')
        last_update = exchange_rates_status.data.get('updated')

        from_currency_name = request.query_params.get('from')
        to_currency_name = request.query_params.get('to')
        for currency_name in [from_currency_name, to_currency_name]:
            if currency_name not in exchange_rates:
                return Response(
                    data={'error': f'The currency [{currency_name}] is not available for conversion.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        from_currency = exchange_rates[from_currency_name]
        to_currency = exchange_rates[to_currency_name]

        amount_str = request.query_params.get('amount')
        try:
            amount = float(amount_str)
        except ValueError:
                return Response(
                    data={'error': f'The amount [{amount_str}] is a invalid value.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        converted_value = amount * to_currency / from_currency

        response = {
            'from_currency': from_currency_name,
            'amount': amount,
            'to_currency': to_currency_name,
            'converted_value': converted_value,
            'last_update': last_update,
        }
        return Response(data=response)


class CacheClear(APIView):
    """Cache clear utility"""

    def post(self, request):
        """Clear Django cache for manual tests purpose."""
        cache = caches['default']
        result = cache.clear()
        return Response(data={'cache_cleared': result})
