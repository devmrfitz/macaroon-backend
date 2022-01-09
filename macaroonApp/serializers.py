from rest_framework import serializers

from macaroonApp.models import Profile, CustomGroup


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
