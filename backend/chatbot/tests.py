"""
Unit tests for chatbot application.
Tests FAQMatcher algorithm, API views, and model interactions.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
import json

from .models import Conversation, Message, HumanHandoffRequest
from .ai_matcher import FAQMatcher
from faq.models import FAQ


class FAQMatcherTestCase(TestCase):
    """Test FAQMatcher algorithm."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.matcher = FAQMatcher()
        
        # Create test FAQs
        FAQ.objects.create(
            question="What is astrology?",
            answer="Astrology is the study of celestial bodies.",
            keywords=['astrology', 'study', 'celestial'],
            category='Basic'
        )
        
        FAQ.objects.create(
            question="How do I get a birth chart reading?",
            answer="You can book a reading through our website.",
            keywords=['birth', 'chart', 'reading', 'booking'],
            category='Services'
        )
    
    def test_preprocess_text(self):
        """Test text preprocessing."""
        text = "What Is ASTROLOGY???"
        cleaned = self.matcher.preprocess_text(text)
        self.assertEqual(cleaned, "what is astrology")
    
    def test_extract_keywords(self):
        """Test keyword extraction."""
        text = "Tell me about astrology and birth charts"
        keywords = self.matcher.extract_keywords(text)
        
        # Should not include stopwords (me, about, and, and)
        self.assertIn('astrology', keywords)
        self.assertIn('birth', keywords)
        self.assertIn('charts', keywords)
        self.assertNotIn('and', keywords)
        self.assertNotIn('me', keywords)
    
    def test_similarity_exact_match(self):
        """Test similarity for exact matches."""
        text1 = "What is astrology?"
        text2 = "What is astrology?"
        similarity = self.matcher.calculate_similarity(text1, text2)
        
        self.assertGreater(similarity, 0.8)
    
    def test_similarity_similar_text(self):
        """Test similarity for similar but not identical text."""
        text1 = "How to get a birth chart reading"
        text2 = "Can I book a birth chart reading?"
        similarity = self.matcher.calculate_similarity(text1, text2)
        
        # Should have decent similarity
        self.assertGreater(similarity, 0.5)
    
    def test_similarity_dissimilar_text(self):
        """Test similarity for dissimilar text."""
        text1 = "What is astrology?"
        text2 = "Tell me about pizza recipes"
        similarity = self.matcher.calculate_similarity(text1, text2)
        
        self.assertLess(similarity, 0.3)
    
    def test_keyword_match_score(self):
        """Test keyword matching."""
        user_text = "I want astrology and birth chart"
        faq_keywords = ['astrology', 'birth', 'chart']
        
        score = self.matcher.keyword_match_score(user_text, faq_keywords)
        self.assertGreater(score, 0.5)
    
    def test_get_response_with_match(self):
        """Test getting response with matching FAQ."""
        user_message = "Tell me about astrology"
        response = self.matcher.get_response(user_message)
        
        self.assertTrue(response.get('success'))
        self.assertIn('answer', response.get('response', '').lower())
    
    def test_get_response_no_match(self):
        """Test getting response with no matching FAQ."""
        user_message = "Tell me about pizza and cooking recipes"
        response = self.matcher.get_response(user_message)
        
        # Should still return a response but with low confidence
        self.assertIn('response', response)


class ChatAPITestCase(APITestCase):
    """Test Chat API endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
        
        # Create test FAQ
        self.faq = FAQ.objects.create(
            question="What is your service?",
            answer="We provide astrology services.",
            keywords=['service', 'astrology'],
            category='General'
        )
    
    def test_chat_message_empty(self):
        """Test chat endpoint with empty message."""
        url = reverse('chat')
        data = {
            'session_id': 'test-session-1',
            'message': '',
            'language': 'en'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_chat_message_valid(self):
        """Test chat endpoint with valid message."""
        url = reverse('chat')
        data = {
            'session_id': 'test-session-1',
            'message': 'What service do you provide?',
            'language': 'en'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('ai_response', response.data)
        self.assertIn('session_id', response.data)
        self.assertEqual(response.data['session_id'], 'test-session-1')
    
    def test_conversation_persistence(self):
        """Test that messages are persisted in database."""
        url = reverse('chat')
        session_id = 'test-session-persistent'
        
        # Send first message
        data = {
            'session_id': session_id,
            'message': 'Hello',
            'language': 'en'
        }
        response1 = self.client.post(url, data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Verify conversation was created
        conversation = Conversation.objects.get(session_id=session_id)
        self.assertEqual(conversation.language, 'en')
        
        # Verify messages were saved
        messages = Message.objects.filter(conversation=conversation)
        self.assertGreaterEqual(messages.count(), 2)  # User + AI response


class HumanHandoffTestCase(APITestCase):
    """Test human handoff workflow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.conversation = Conversation.objects.create(
            session_id='test-handoff-session',
            language='en'
        )
    
    def test_handoff_request_creation(self):
        """Test creating a handoff request."""
        url = reverse('request_human')
        data = {
            'session_id': 'test-handoff-session',
            'name': 'John Doe',
            'phone': '+1234567890',
            'problem_summary': 'Unable to book an appointment'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('ticket_id', response.data)
    
    def test_handoff_request_duplicate_prevention(self):
        """Test that duplicate pending requests are prevented."""
        # Create first handoff request
        handoff1 = HumanHandoffRequest.objects.create(
            conversation=self.conversation,
            name='John Doe',
            phone='+1234567890',
            problem_summary='Issue 1',
            status='pending'
        )
        
        # Try to create another for same conversation
        url = reverse('request_human')
        data = {
            'session_id': 'test-handoff-session',
            'name': 'Jane Doe',
            'phone': '+0987654321',
            'problem_summary': 'Issue 2'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return existing request info
        self.assertIn('already in queue', response.data['message'])
    
    def test_handoff_invalid_session(self):
        """Test handoff with invalid session."""
        url = reverse('request_human')
        data = {
            'session_id': 'nonexistent-session',
            'name': 'John Doe',
            'phone': '+1234567890',
            'problem_summary': 'Issue'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class ConversationHistoryTestCase(APITestCase):
    """Test conversation history retrieval."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.conversation = Conversation.objects.create(
            session_id='test-history-session',
            language='en'
        )
        
        # Add test messages
        Message.objects.create(
            conversation=self.conversation,
            content='Hello',
            is_user=True
        )
        
        Message.objects.create(
            conversation=self.conversation,
            content='Hi there!',
            is_user=False
        )
    
    def test_get_conversation_history(self):
        """Test retrieving conversation history."""
        url = reverse('conversation_history')
        response = self.client.get(url, {'session_id': 'test-history-session'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['session_id'], 'test-history-session')
        self.assertEqual(len(response.data['messages']), 2)
    
    def test_get_history_missing_session_id(self):
        """Test that session_id parameter is required."""
        url = reverse('conversation_history')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_get_history_nonexistent_session(self):
        """Test retrieving history for nonexistent session."""
        url = reverse('conversation_history')
        response = self.client.get(url, {'session_id': 'nonexistent'})
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)


class ConversationModelTestCase(TestCase):
    """Test Conversation model."""
    
    def test_conversation_creation(self):
        """Test creating a conversation."""
        conv = Conversation.objects.create(
            session_id='test-session',
            language='en'
        )
        
        self.assertEqual(conv.session_id, 'test-session')
        self.assertEqual(conv.language, 'en')
        self.assertIsNotNone(conv.created_at)
    
    def test_conversation_last_active_update(self):
        """Test that last_active is updated."""
        conv = Conversation.objects.create(
            session_id='test-session',
            language='en'
        )
        
        original_active = conv.last_active
        
        # Trigger update
        conv.save()
        
        self.assertGreaterEqual(conv.last_active, original_active)


class MessageModelTestCase(TestCase):
    """Test Message model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.conversation = Conversation.objects.create(
            session_id='test-session',
            language='en'
        )
    
    def test_message_creation(self):
        """Test creating a message."""
        msg = Message.objects.create(
            conversation=self.conversation,
            content='Test message',
            is_user=True
        )
        
        self.assertEqual(msg.content, 'Test message')
        self.assertTrue(msg.is_user)
        self.assertIsNotNone(msg.timestamp)
    
    def test_message_ordering(self):
        """Test that messages are ordered by timestamp."""
        msg1 = Message.objects.create(
            conversation=self.conversation,
            content='First',
            is_user=True
        )
        
        msg2 = Message.objects.create(
            conversation=self.conversation,
            content='Second',
            is_user=False
        )
        
        messages = Message.objects.filter(conversation=self.conversation)
        self.assertEqual(messages[0].content, 'First')
        self.assertEqual(messages[1].content, 'Second')
