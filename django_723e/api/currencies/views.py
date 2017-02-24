"""
    currencies
"""
from django_723e.models.currency.models import Currency
from django_723e.models.currency.serializers import CurrencySerializer

from rest_framework import viewsets

class CurrenciesList(viewsets.ReadOnlyModelViewSet):
    """
        CRUD access to Currency models
    """
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer