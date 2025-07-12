"""
Email notification channel implementation
"""

import os
from datetime import datetime
from typing import Dict, Any
from src.channels.base import NotificationChannel
from src.core.models import NotificationResult, ChannelError


class EmailChannel(NotificationChannel):
    """Email channel that writes messages to files (mock implementation)"""
    
    def __init__(self, output_dir: str = "email_outputs"):
        """
        Initialize the email channel
        
        Args:
            output_dir: Directory to write email files to
        """
        self.output_dir = output_dir
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """Ensure the output directory exists"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    @property
    def channel_name(self) -> str:
        return "email"
    
    def validate_recipient(self, recipient: str) -> bool:
        """Validate email address format"""
        return bool(recipient and "@" in recipient and "." in recipient.split("@")[1])
    
    def send(self, message: str, recipient: str, **kwargs) -> NotificationResult:
        """
        Send email by writing to a file
        
        Args:
            message: The email message content
            recipient: Email address of the recipient
            **kwargs: Additional parameters (subject, from_email, etc.)
            
        Returns:
            NotificationResult: Result of the send operation
        """
        try:
            if not self.validate_recipient(recipient):
                raise ChannelError(f"Invalid email recipient: {recipient}")
            
            # Create filename based on timestamp and recipient
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_recipient = recipient.replace("@", "_at_").replace(".", "_")
            filename = f"{timestamp}_{safe_recipient}.txt"
            filepath = os.path.join(self.output_dir, filename)
            
            # Prepare email content
            subject = kwargs.get("subject", "Notification")
            from_email = kwargs.get("from_email", "noreply@notification-service.com")
            
            email_content = self._format_email(from_email, recipient, subject, message)
            
            # Write to file
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(email_content)
            
            return NotificationResult(
                success=True,
                message=f"Email written to {filepath}",
                channel=self.channel_name,
                recipient=recipient
            )
            
        except Exception as e:
            return NotificationResult(
                success=False,
                message=f"Failed to send email: {str(e)}",
                channel=self.channel_name,
                recipient=recipient,
                error=str(e)
            )
    
    def _format_email(self, from_email: str, to_email: str, subject: str, message: str) -> str:
        """Format the email content"""
        return f"""From: {from_email}
To: {to_email}
Subject: {subject}
Date: {datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")}

{message}
"""
    
    def prepare_message(self, message: str, metadata: Dict[str, Any]) -> str:
        """Prepare email message with any special formatting"""
        # Add email-specific formatting if needed
        return message
