from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from macaroonApp.models import Profile, CustomGroup, Transaction, FinalPayment


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='user.email')
    user = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = Profile
        fields = ['id', 'First_Name', 'Last_Name', 'public_key', 'user', 'email', 'contacts']
        read_only_fields = ['id']


class CustomGroupSerializer(serializers.ModelSerializer):
    members = ProfileSerializer(many=True, read_only=True)

    class Meta:
        model = CustomGroup
        fields = ['id', 'name', 'description', 'slug', 'members']
        read_only_fields = ['id', 'members']


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = ['id', 'sender', 'intermediary', 'amount', 'timestamp', "contract_address", "destination", "message", "expiry"]
        read_only_fields = ['id', ]


class FinalPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinalPayment
        fields = ['id', 'moneySender', 'moneyReceiver', 'amount', 'timestamp', 'message']
        read_only_fields = ['id', ]
