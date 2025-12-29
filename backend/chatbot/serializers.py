from rest_framework import serializers
from .models import Conversation, Message, HumanHandoffRequest

class ChatMessageSerializer(serializers.Serializer):
    session_id = serializers.CharField(max_length=100, required=True)
    message = serializers.CharField(required=True)
    language = serializers.CharField(max_length=10, default='en')

class HumanHandoffSerializer(serializers.Serializer):
    session_id = serializers.CharField(max_length=100, required=True)
    name = serializers.CharField(max_length=100, required=True)
    phone = serializers.CharField(max_length=20, required=True)
    problem_summary = serializers.CharField(required=True)
    
    def validate_phone(self, value):
        # Basic phone validation
        if not value.replace('+', '').replace(' ', '').isdigit():
            raise serializers.ValidationError("Please enter a valid phone number")
        return value

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ['id', 'session_id', 'language', 'created_at', 'last_active']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'content', 'is_user', 'timestamp']
