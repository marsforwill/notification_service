"""
Slack notification channel implementation
"""

from datetime import datetime
from typing import Dict, Any
from src.channels.base import NotificationChannel
from src.core.models import NotificationResult, ChannelError


class SlackChannel(NotificationChannel):
    """Slack channel that prints messages to console (mock implementation)"""
    
    def __init__(self):
        """Initialize the Slack channel"""
        pass
    
    @property
    def channel_name(self) -> str:
        return "slack"
    
    def validate_recipient(self, recipient: str) -> bool:
        """Validate Slack channel or user format"""
        return bool(recipient and (recipient.startswith("#") or recipient.startswith("@")))
    
    def send(self, message: str, recipient: str, **kwargs) -> NotificationResult:
        """
        Send Slack message by printing to console
        
        Args:
            message: The Slack message content
            recipient: Channel (#channel) or user (@user) identifier
            **kwargs: Additional parameters (username, icon_emoji, etc.)
            
        Returns:
            NotificationResult: Result of the send operation
        """
        try:
            if not self.validate_recipient(recipient):
                raise ChannelError(f"Invalid Slack recipient: {recipient}")
            
            # Prepare Slack message format
            username = kwargs.get("username", "Notification Bot")
            icon_emoji = kwargs.get("icon_emoji", ":bell:")
            
            formatted_message = self._format_slack_message(
                recipient, username, icon_emoji, message
            )
            
            # Print to console (mock Slack API call)
            print(formatted_message)
            
            return NotificationResult(
                success=True,
                message=f"Slack message sent to {recipient}",
                channel=self.channel_name,
                recipient=recipient
            )
            
        except Exception as e:
            return NotificationResult(
                success=False,
                message=f"Failed to send Slack message: {str(e)}",
                channel=self.channel_name,
                recipient=recipient,
                error=str(e)
            )
    
    def _format_slack_message(self, recipient: str, username: str, icon_emoji: str, message: str) -> str:
        """Format the Slack message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return f"""
🔔 [SLACK MESSAGE] {timestamp}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Channel: {recipient}
Bot: {username} {icon_emoji}
Message: {message}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    def prepare_message(self, message: str, metadata: Dict[str, Any]) -> str:
        """Prepare Slack message with any special formatting"""
        # Add Slack-specific formatting (e.g., markdown)
        return message
