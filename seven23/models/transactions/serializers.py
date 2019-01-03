"""
    Serialized for transactions module
"""
from rest_framework import serializers
from seven23.models.accounts.models import Account
from seven23.models.currency.models import Currency
from seven23.models.categories.models import Category
from seven23.models.transactions.models import DebitsCredits, Change

from rest_framework_bulk import (
    BulkListSerializer,
    BulkSerializerMixin,
    ListBulkCreateUpdateDestroyAPIView,
)

class DebitsCreditsSerializer(serializers.HyperlinkedModelSerializer):
    """
        Serialized for DebitsCredits model
    """
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())

    class Meta:
        model = DebitsCredits
        fields = ('id', 'account', 'blob', 'active', 'last_edited', 'deleted')


class DebitsCreditsSerializerList(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    """
        Serialized for DebitsCredits model
    """
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())

    class Meta:
        model = DebitsCredits
        list_serializer_class = BulkListSerializer
        fields = ('id', 'account', 'blob', 'active', 'last_edited', 'deleted')



class ChangeSerializer(serializers.HyperlinkedModelSerializer):
    """
        Serializer for Change model
    """
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())

    class Meta:
        model = Change
        fields = ('id', 'account', 'blob', 'active', 'last_edited', 'deleted')