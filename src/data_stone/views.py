from django.http import HttpResponse
from django.views import View

class Test(View):
    """Simple test view."""

    def get(self, request):
        """Simple test get."""
        return HttpResponse("It's working.")
