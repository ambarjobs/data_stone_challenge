from django.conf import settings
from django.core.cache import caches
from django.db import models


CURRENCY_ACRONYMS_SIZE = 3
CACHE_KEY = 'api_models_concurrency'


class Currency(models.Model):
    """Available currencies."""
    acronym = models.CharField(max_length=CURRENCY_ACRONYMS_SIZE, null=False, blank=False)     # type: ignore[var-annotated]

    class Meta:
        verbose_name_plural = 'currencies'

    def __str__(self) -> str:
        """Return object string representation."""
        return self.acronym

    def save(self, *args, **kwargs):
        """Override `save()` to ensure `acronym` is upper case."""
        if not str(self.acronym).isalpha():
            return
        self.acronym = self.acronym.upper()
        super().save(*args, **kwargs)

    @classmethod
    def cached_acronyms_list(cls) -> list[str]:
        """Return a cached list of currencies."""
        cache = caches['default']
        acronyms_list = cache.get(key=CACHE_KEY)
        if acronyms_list is None:
            acronyms_list = list(cls.objects.values_list('acronym', flat=True))
            cache.set(
                key=CACHE_KEY,
                value=acronyms_list,
                timeout=settings.ACRONYMS_LIST_CACHE_TIMEOUT
            )
        return acronyms_list
