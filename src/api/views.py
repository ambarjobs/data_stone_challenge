from rest_framework.response import Response
from rest_framework.views import APIView

class Conversion(APIView):
    """Conversion resource."""

    def get(self, request):
        """Get currency conversion."""
        data = {'result': 'ok'}
        return Response(data=data)
