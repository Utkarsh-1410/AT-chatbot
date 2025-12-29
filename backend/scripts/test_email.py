"""
Test Email Notification Configuration
Run this script to verify your email settings are working correctly.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'astrotamil_api.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings


def test_email_configuration():
    """Test email notification settings."""
    
    print("=" * 60)
    print("AstroTamil Email Configuration Test")
    print("=" * 60)
    
    # Check configuration
    print("\n📧 Email Settings:")
    print(f"   Backend: {settings.EMAIL_BACKEND}")
    print(f"   Host: {settings.EMAIL_HOST}")
    print(f"   Port: {settings.EMAIL_PORT}")
    print(f"   TLS: {settings.EMAIL_USE_TLS}")
    print(f"   User: {settings.EMAIL_HOST_USER}")
    print(f"   From: {settings.DEFAULT_FROM_EMAIL}")
    
    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        print("\n❌ ERROR: Email credentials not configured!")
        print("\nPlease set the following environment variables:")
        print("   - EMAIL_HOST_USER")
        print("   - EMAIL_HOST_PASSWORD")
        print("   - ADMIN_EMAIL (recipient)")
        return False
    
    admin_email = os.getenv('ADMIN_EMAIL', '')
    if not admin_email:
        print("\n❌ ERROR: ADMIN_EMAIL not set!")
        print("Set ADMIN_EMAIL environment variable to receive test email.")
        return False
    
    print(f"\n📬 Recipient: {admin_email}")
    
    # Send test email
    print("\n📤 Sending test email...")
    try:
        send_mail(
            subject='AstroTamil - Test Email Notification',
            message=(
                'This is a test email from AstroTamil Customer Care Assistant.\n\n'
                'If you received this email, your notification system is working correctly!\n\n'
                '✅ Configuration Status: SUCCESS\n'
                'Email notifications for human handoff requests are now active.'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_email],
            fail_silently=False,
        )
        
        print("✅ Test email sent successfully!")
        print(f"\nCheck your inbox at: {admin_email}")
        print("\nNote: It may take a few seconds to arrive.")
        print("Check spam folder if you don't see it in inbox.")
        return True
        
    except Exception as e:
        print(f"\n❌ Failed to send email: {str(e)}")
        print("\nCommon issues:")
        print("   - Incorrect email/password")
        print("   - 2FA enabled but no app password (Gmail)")
        print("   - Firewall blocking SMTP port")
        print("   - Invalid SMTP server settings")
        return False


if __name__ == '__main__':
    success = test_email_configuration()
    print("\n" + "=" * 60)
    sys.exit(0 if success else 1)
