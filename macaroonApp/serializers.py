from rest_framework import serializers

from macaroonApp.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='user.email')
    user = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = Profile
        fields = ['id', 'First_Name', 'Last_Name', 'public_key', 'user', 'email']
        read_only_fields = ['id']
