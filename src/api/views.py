import rest_framework.status as status
from rest_framework.response import Response
from rest_framework.views import APIView

from .logic import ExchangeApi

class Conversion(APIView):
    """Conversion resource."""

    def get(self, request):
        """Get currency conversion."""
        exchange_api = ExchangeApi()

        exchange_rates = exchange_api.get_exchange_rates()

        if exchange_rates.error:
            return Response(data=exchange_rates.data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=exchange_rates.data)
