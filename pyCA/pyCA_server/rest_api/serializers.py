from rest_framework import serializers
from rest_api.models import Message


class MessageSerializer(serializers.ModelSerializer):
	class Meta:
		model = Message
		fields = ['id', 'message']