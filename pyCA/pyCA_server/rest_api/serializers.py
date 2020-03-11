from django.contrib.auth.models import User
from rest_framework import serializers
from rest_api.models import Message


class MessageSerializer(serializers.ModelSerializer):	
	owner = serializers.ReadOnlyField(source='owner.username')
	
	class Meta:
		model = Message
		fields = ['id', 'created', 'owner', 'message']


class UserSerializer(serializers.ModelSerializer):
	messages = serializers.PrimaryKeyRelatedField(many=True, queryset=Message.objects.all())

	class Meta:
		model = User
		fields = ['id', 'username', 'messages']
