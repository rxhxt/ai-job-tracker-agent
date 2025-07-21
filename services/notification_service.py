"""
Email notification service for job-related updates.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from datetime import datetime

from models.job_application import NotificationData, EmailData, EmailType
from config.settings import settings

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for sending email notifications."""
    
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.email_address = settings.EMAIL_ADDRESS
        self.email_password = settings.EMAIL_PASSWORD
        self.notification_emails = settings.NOTIFICATION_EMAILS
    
    def send_interview_notification(self, email_data: EmailData) -> bool:
        """
        Send notification for interview invitation.
        
        Args:
            email_data: EmailData containing interview information
            
        Returns:
            True if successful, False otherwise
        """
        subject = f"🎯 Interview Invitation: {email_data.company} - {email_data.position}"
        
        body = f"""
Great news! You have received an interview invitation.

Company: {email_data.company}
Position: {email_data.position}
Email Subject: {email_data.subject}
Received: {email_data.date.strftime('%Y-%m-%d %H:%M')}

Original Email Preview:
{email_data.body[:500]}...

Please check your email for full details and respond promptly.

Best of luck!
Your Job AI Agent
"""
        
        return self._send_email(subject, body, "interview")
    
    def send_assessment_notification(self, email_data: EmailData) -> bool:
        """
        Send notification for assessment request.
        
        Args:
            email_data: EmailData containing assessment information
            
        Returns:
            True if successful, False otherwise
        """
        subject = f"📝 Assessment Request: {email_data.company} - {email_data.position}"
        
        body = f"""
You have received an assessment request!

Company: {email_data.company}
Position: {email_data.position}
Email Subject: {email_data.subject}
Received: {email_data.date.strftime('%Y-%m-%d %H:%M')}

Original Email Preview:
{email_data.body[:500]}...

Please check your email for full details and complete the assessment as soon as possible.

Good luck!
Your Job AI Agent
"""
        
        return self._send_email(subject, body, "assessment")
    
    def send_rejection_notification(self, email_data: EmailData) -> bool:
        """
        Send notification for job rejection (optional).
        
        Args:
            email_data: EmailData containing rejection information
            
        Returns:
            True if successful, False otherwise
        """
        subject = f"❌ Job Application Update: {email_data.company} - {email_data.position}"
        
        body = f"""
Your job application status has been updated.

Company: {email_data.company}
Position: {email_data.position}
Status: Rejected
Email Subject: {email_data.subject}
Received: {email_data.date.strftime('%Y-%m-%d %H:%M')}

Don't be discouraged! Keep applying and something great will come along.

Stay positive!
Your Job AI Agent
"""
        
        return self._send_email(subject, body, "rejection")
    
    def send_daily_summary(self, new_applications: int, updates: int, interviews: int, assessments: int) -> bool:
        """
        Send daily summary of job tracking activity.
        
        Args:
            new_applications: Number of new applications found
            updates: Number of status updates
            interviews: Number of interview invitations
            assessments: Number of assessment requests
            
        Returns:
            True if successful, False otherwise
        """
        subject = f"📊 Daily Job Tracking Summary - {datetime.now().strftime('%Y-%m-%d')}"
        
        body = f"""
Here's your daily job tracking summary:

📝 New Applications Found: {new_applications}
🔄 Status Updates: {updates}
🎯 Interview Invitations: {interviews}
📝 Assessment Requests: {assessments}

Your job search is being actively monitored. Keep up the great work!

Best regards,
Your Job AI Agent
"""
        
        return self._send_email(subject, body, "summary")
    
    def _send_email(self, subject: str, body: str, notification_type: str) -> bool:
        """
        Send email notification.
        
        Args:
            subject: Email subject
            body: Email body
            notification_type: Type of notification for logging
            
        Returns:
            True if successful, False otherwise
        """
        if not self.notification_emails:
            logger.warning("No notification emails configured")
            return False
        
        if not all([self.email_address, self.email_password]):
            logger.error("Email credentials not configured")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = ', '.join(self.notification_emails)
            msg['Subject'] = subject
            
            # Attach body
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            
            logger.info(f"Sent {notification_type} notification to {len(self.notification_emails)} recipients")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed - check email credentials")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending {notification_type} notification: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending {notification_type} notification: {e}")
            return False
    
    def test_email_configuration(self) -> bool:
        """
        Test email configuration by sending a test message.
        
        Returns:
            True if test successful or email disabled, False if enabled but failed
        """
        # Check if email notifications are disabled
        if not self.email_address or not self.email_password or not self.notification_emails:
            logger.info("Email notifications disabled - skipping configuration test")
            return True
            
        subject = "🧪 Job AI Agent - Email Configuration Test"
        body = """
This is a test email from your Job AI Agent.

If you receive this message, your email notification configuration is working correctly!

Your Job AI Agent is now ready to monitor your job applications and send you important updates.

Best regards,
Your Job AI Agent
"""
        
        success = self._send_email(subject, body, "test")
        if success:
            logger.info("Email configuration test successful")
        else:
            logger.error("Email configuration test failed")
        
        return success
    
    def should_send_notification(self, email_data: EmailData) -> bool:
        """
        Determine if a notification should be sent for this email.
        
        Args:
            email_data: EmailData to evaluate
            
        Returns:
            True if notification should be sent
        """
        # Send notifications for high-priority emails
        high_priority_types = [
            EmailType.INTERVIEW_INVITATION,
            EmailType.ASSESSMENT_REQUEST
        ]
        
        return (
            email_data.email_type in high_priority_types and
            email_data.confidence > 0.6 and
            email_data.company and
            email_data.position
        )
    
    def send_notification_for_email(self, email_data: EmailData) -> bool:
        """
        Send appropriate notification based on email type.
        
        Args:
            email_data: EmailData to send notification for
            
        Returns:
            True if successful, False otherwise
        """
        if not self.should_send_notification(email_data):
            return False
        
        if email_data.email_type == EmailType.INTERVIEW_INVITATION:
            return self.send_interview_notification(email_data)
        elif email_data.email_type == EmailType.ASSESSMENT_REQUEST:
            return self.send_assessment_notification(email_data)
        else:
            logger.debug(f"No notification handler for email type: {email_data.email_type}")
            return False
