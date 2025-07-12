"""
Base notification channel interface
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from src.core.models import NotificationResult


class NotificationChannel(ABC):
    """Abstract base class for notification channels"""
    
    @abstractmethod
    def send(self, message: str, recipient: str, **kwargs) -> NotificationResult:
        """
        Send a notification message to the recipient
        
        Args:
            message: The formatted message to send
            recipient: The recipient identifier (email, channel, etc.)
            **kwargs: Additional channel-specific parameters
            
        Returns:
            NotificationResult: Result of the send operation
        """
        pass
    
    @property
    @abstractmethod
    def channel_name(self) -> str:
        """Return the name of this channel"""
        pass
    
    def validate_recipient(self, recipient: str) -> bool:
        """
        Validate if the recipient is valid for this channel
        
        Args:
            recipient: The recipient identifier
            
        Returns:
            bool: True if valid, False otherwise
        """
        return bool(recipient and recipient.strip())
    
    def prepare_message(self, message: str, metadata: Dict[str, Any]) -> str:
        """
        Prepare the message for sending (optional preprocessing)
        
        Args:
            message: The original message
            metadata: Additional metadata
            
        Returns:
            str: The prepared message
        """
        return message
