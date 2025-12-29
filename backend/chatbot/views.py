from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

from .models import Conversation, Message, HumanHandoffRequest
from .ai_matcher import FAQMatcher
from .notifications import NotificationService
from .serializers import (
    ChatMessageSerializer, 
    HumanHandoffSerializer,
    ConversationSerializer
)

class ChatAPIView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.faq_matcher = FAQMatcher()
    
    def post(self, request):
        session_id = request.data.get('session_id')
        user_message = request.data.get('message', '').strip()
        language = request.data.get('language', 'en')
        
        # Generate session_id if None or empty
        if not session_id:
            session_id = f"auto_{timezone.now().timestamp()}_{id(request)}"
        
        if not user_message:
            return Response({
                'error': 'Message cannot be empty'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create conversation
        conversation, created = Conversation.objects.get_or_create(
            session_id=session_id,
            defaults={
                'language': language,
                'created_at': timezone.now()
            }
        )
        
        # Update last active time
        conversation.last_active = timezone.now()
        conversation.save()
        
        # Save user message
        user_msg = Message.objects.create(
            conversation=conversation,
            content=user_message,
            is_user=True
        )
        
        # Check if this is a response to human handoff prompt
        # Load last few messages and check if last AI message asked for human agent
        recent_qs = Message.objects.filter(conversation=conversation).order_by('-timestamp')[:5]
        last_messages = list(recent_qs)

        needs_human_response = False
        if len(last_messages) > 1:
            # find the most recent AI message within the recent slice
            last_ai_msg = next((m for m in last_messages if not m.is_user), None)
            if last_ai_msg and 'human agent' in last_ai_msg.content.lower():
                # User is responding to human agent prompt
                if any(k in user_message.lower() for k in ('yes', 'ok', 'sure')):
                    needs_human_response = True
        
        if needs_human_response:
            ai_response = {
                'success': False,
                'response': "Please provide your details so our human agent can contact you:\n\n1. Your Name\n2. Contact Number\n3. Brief summary of your issue",
                'type': 'collect_human_details'
            }
        else:
            # Get AI response
            ai_response = self.faq_matcher.get_response(user_message)
        
        # Save AI response
        ai_msg = Message.objects.create(
            conversation=conversation,
            content=ai_response['response'],
            is_user=False
        )
        
        # Prepare response data
        response_data = {
            'session_id': session_id,
            'user_message': user_message,
            'ai_response': ai_response['response'],
            'response_type': ai_response.get('type', 'unknown'),
            'confidence': ai_response.get('confidence', 0),
            'timestamp': timezone.now().isoformat()
        }
        
        if ai_response.get('success'):
            response_data.update({
                'matched_question': ai_response.get('question'),
                'category': ai_response.get('category')
            })
        
        return Response(response_data)

class RequestHumanAgentView(APIView):
    def post(self, request):
        serializer = HumanHandoffSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                conversation = Conversation.objects.get(
                    session_id=serializer.validated_data['session_id']
                )
                
                # Check if already exists
                existing_request = HumanHandoffRequest.objects.filter(
                    conversation=conversation,
                    status='pending'
                ).first()
                
                if existing_request:
                    return Response({
                        'success': True,
                        'message': 'Your request is already in queue. An agent will contact you shortly.',
                        'ticket_id': existing_request.id,
                        'status': existing_request.status
                    })
                
                # Create new request
                handoff_request = HumanHandoffRequest.objects.create(
                    conversation=conversation,
                    name=serializer.validated_data['name'],
                    phone=serializer.validated_data['phone'],
                    problem_summary=serializer.validated_data['problem_summary']
                )
                
                # Send notification to admin/agent
                NotificationService.send_agent_notification(handoff_request)
                
                return Response({
                    'success': True,
                    'message': 'Your request has been submitted. A human agent will contact you within 24 hours.',
                    'ticket_id': handoff_request.id,
                    'reference_number': str(handoff_request.id)[:8].upper()
                })
                
            except Conversation.DoesNotExist:
                return Response({
                    'error': 'Invalid session'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ConversationHistoryView(APIView):
    def get(self, request):
        session_id = request.query_params.get('session_id')
        
        if not session_id:
            return Response({
                'error': 'session_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            conversation = Conversation.objects.get(session_id=session_id)
            messages = Message.objects.filter(
                conversation=conversation
            ).order_by('timestamp')
            
            messages_data = []
            for msg in messages:
                messages_data.append({
                    'id': str(msg.id),
                    'content': msg.content,
                    'is_user': msg.is_user,
                    'timestamp': msg.timestamp.isoformat()
                })
            
            return Response({
                'session_id': session_id,
                'conversation_id': str(conversation.id),
                'messages': messages_data,
                'total_messages': len(messages_data)
            })
            
        except Conversation.DoesNotExist:
            return Response({
                'error': 'Conversation not found'
            }, status=status.HTTP_404_NOT_FOUND)
