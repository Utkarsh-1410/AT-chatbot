from django.urls import path
from .views import ChatAPIView, RequestHumanAgentView, ConversationHistoryView

urlpatterns = [
    path('chat/', ChatAPIView.as_view(), name='chat'),
    path('request-human/', RequestHumanAgentView.as_view(), name='request_human'),
    path('conversation-history/', ConversationHistoryView.as_view(), name='conversation_history'),
]
