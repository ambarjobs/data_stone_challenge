# ==================================================================================================
#   `api` serializers
# ==================================================================================================

from rest_framework import serializers as srlz

# --------------------------------------------------------------------------------------------------
#   Validation
# --------------------------------------------------------------------------------------------------
def greater_than_zero_validator(value):
    """Serializer validation for value must be greater than 0."""
    if value <= 0:
        raise srlz.ValidationError('Invalid rate: must be > 0.0')

# --------------------------------------------------------------------------------------------------
#   Input serializers
# --------------------------------------------------------------------------------------------------
class ExchangeApiInputSerializer(srlz.Serializer):
    """External exchange API input validation."""
    lastupdate = srlz.DateTimeField(input_formats=['iso-8601'])
    rates = srlz.DictField(child=srlz.FloatField(validators=[greater_than_zero_validator]))
