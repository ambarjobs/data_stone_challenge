# ==================================================================================================
#   `api` urls
# ==================================================================================================

from django.urls import path

from . import views


urlpatterns = [
    path('currency/conversion/', views.Conversion.as_view(), name='api.currency_conversion'),
    path('cache/clear/', views.CacheClear.as_view(), name='api.cache_clear'),
]
