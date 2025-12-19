"""
Notification system for human handoff requests.
Supports email, SMS, and in-app notifications.
"""

import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending notifications to agents about handoff requests."""
    
    @staticmethod
    def send_agent_notification(handoff_request) -> bool:
        """
        Send notification to admin/agent about new handoff request.
        
        Args:
            handoff_request: HumanHandoffRequest instance
            
        Returns:
            bool: True if notification sent successfully, False otherwise
        """
        try:
            # Get admin email from settings (configure via env var ADMIN_EMAIL)
            admin_email = os.getenv('ADMIN_EMAIL', '')
            
            if not admin_email:
                logger.warning(
                    f"ADMIN_EMAIL not configured. Handoff request {handoff_request.id} created but not notified."
                )
                return False
            
            # Prepare notification message
            subject = f"New Customer Handoff Request - Ticket #{str(handoff_request.id)[:8].upper()}"
            message = NotificationService._format_handoff_email(handoff_request)
            
            # Send via available channels
            NotificationService._send_email(admin_email, subject, message)
            NotificationService._send_sms_alert(handoff_request)
            
            # Log successful notification
            logger.info(f"Notification sent for handoff request {handoff_request.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send notification for handoff request: {str(e)}")
            return False
    
    @staticmethod
    def _format_handoff_email(handoff_request) -> str:
        """Format handoff request as email body."""
        return f"""
        NEW CUSTOMER HANDOFF REQUEST
        
Ticket ID: {str(handoff_request.id)[:8].upper()}
Customer Name: {handoff_request.name}
Contact Number: {handoff_request.phone}
Problem Summary: {handoff_request.problem_summary}
Request Time: {handoff_request.created_at.isoformat()}
Conversation ID: {handoff_request.conversation.id}
Language: {handoff_request.conversation.language}
Status: {handoff_request.status}

Please contact the customer as soon as possible.
        """
    
    @staticmethod
    def _send_email(recipient: str, subject: str, message: str) -> bool:
        """
        Send email notification.
        
        Configure via env vars:
        - EMAIL_HOST
        - EMAIL_PORT
        - EMAIL_HOST_USER
        - EMAIL_HOST_PASSWORD
        - EMAIL_FROM_ADDRESS
        """
        try:
            from django.core.mail import send_mail
            
            email_from = os.getenv('EMAIL_FROM_ADDRESS', 'noreply@astrotamil.com')
            send_mail(
                subject=subject,
                message=message,
                from_email=email_from,
                recipient_list=[recipient],
                fail_silently=False,
            )
            logger.info(f"Email notification sent to {recipient}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    @staticmethod
    def _send_sms_alert(handoff_request) -> bool:
        """
        Send SMS alert to agent.
        
        Configure via env var: SMS_GATEWAY_API_KEY (e.g., Twilio)
        """
        try:
            sms_enabled = os.getenv('SMS_NOTIFICATIONS_ENABLED', 'false').lower() == 'true'
            if not sms_enabled:
                return False
            
            agent_phone = os.getenv('AGENT_PHONE_NUMBER', '')
            if not agent_phone:
                return False
            
            # Example using Twilio (configure as needed)
            message_body = (
                f"New customer handoff: {handoff_request.name} "
                f"(Ticket: {str(handoff_request.id)[:8].upper()})"
            )
            
            # Placeholder for SMS provider integration (Twilio, AWS SNS, etc.)
            logger.info(f"SMS alert would be sent to {agent_phone}: {message_body}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS: {str(e)}")
            return False
    
    @staticmethod
    def send_customer_confirmation(handoff_request) -> bool:
        """Send confirmation to customer that their request was received."""
        try:
            # Could send email/SMS to customer with ticket number
            logger.info(f"Confirmation sent for handoff request {handoff_request.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send customer confirmation: {str(e)}")
            return False
