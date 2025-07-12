"""
Base deduplication policy interface
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from src.core.models import NotificationEvent, NotificationMessage


class DeduplicationPolicy(ABC):
    """Abstract base class for deduplication policies"""
    
    @abstractmethod
    def should_send(self, message: NotificationMessage, 
                   sent_messages: List[NotificationMessage]) -> bool:
        """
        Determine if a message should be sent based on deduplication policy
        
        Args:
            message: The message to check
            sent_messages: List of previously sent messages
            
        Returns:
            bool: True if message should be sent, False if duplicate
        """
        pass
    
    @abstractmethod
    def get_deduplication_key(self, message: NotificationMessage) -> str:
        """
        Generate a deduplication key for the message
        
        Args:
            message: The message to generate key for
            
        Returns:
            str: Deduplication key
        """
        pass
    
    @property
    @abstractmethod
    def policy_name(self) -> str:
        """Return the name of this deduplication policy"""
        pass
    
    def is_duplicate(self, message: NotificationMessage, 
                    sent_messages: List[NotificationMessage]) -> bool:
        """
        Check if a message is a duplicate
        
        Args:
            message: The message to check
            sent_messages: List of previously sent messages
            
        Returns:
            bool: True if duplicate, False otherwise
        """
        return not self.should_send(message, sent_messages)
    
    def filter_duplicates(self, messages: List[NotificationMessage]) -> List[NotificationMessage]:
        """
        Filter out duplicate messages from a list
        
        Args:
            messages: List of messages to filter
            
        Returns:
            List[NotificationMessage]: List of unique messages
        """
        seen_keys = set()
        unique_messages = []
        
        for message in messages:
            key = self.get_deduplication_key(message)
            if key not in seen_keys:
                seen_keys.add(key)
                unique_messages.append(message)
        
        return unique_messages
