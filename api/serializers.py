from rest_framework import serializers

from .models import Proxy, User, UserAgent


class ProxySerializer(serializers.ModelSerializer):
    class Meta:
        model = Proxy
        fields = "__all__"


class UserAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAgent
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    user_agent = UserAgentSerializer(read_only=True)  # Use UserAgentSerializer
    proxy = ProxySerializer(read_only=True)  # Use ProxySerializer

    class Meta:
        model = User
        fields = "__all__"
