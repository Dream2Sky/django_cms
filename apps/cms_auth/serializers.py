from rest_framework import serializers

from apps.cms_auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("uid", "username", "email", "telephone", "is_active", "is_staff")
