from rest_framework import serializers

from macaroonApp.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='email.email')

    class Meta:
        model = Profile
        fields = ['id', 'First_Name', 'Last_Name', 'public_key',
                  'email']
        read_only_fields = ['id', 'email']
