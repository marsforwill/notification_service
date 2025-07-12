"""
Content-based deduplication policy implementation
"""

import hashlib
from typing import List, Dict, Any
from datetime import datetime, timedelta
from src.deduplication.base import DeduplicationPolicy
from src.core.models import NotificationMessage


class ContentBasedDeduplicationPolicy(DeduplicationPolicy):
    """Deduplication policy based on message content and recipient"""
    
    def __init__(self, time_window_hours: int = 24):
        """
        Initialize the content-based deduplication policy
        
        Args:
            time_window_hours: Time window in hours for considering duplicates
        """
        self.time_window_hours = time_window_hours
        self.sent_messages_cache: Dict[str, List[NotificationMessage]] = {}
    
    @property
    def policy_name(self) -> str:
        return "content_based"
    
    def should_send(self, message: NotificationMessage, 
                   sent_messages: List[NotificationMessage]) -> bool:
        """
        Determine if a message should be sent based on content and time window
        
        Args:
            message: The message to check
            sent_messages: List of previously sent messages
            
        Returns:
            bool: True if message should be sent, False if duplicate
        """
        # Get the deduplication key for this message
        current_key = self.get_deduplication_key(message)
        
        # Check against recent messages within time window
        cutoff_time = datetime.now() - timedelta(hours=self.time_window_hours)
        
        for sent_message in sent_messages:
            if sent_message.timestamp >= cutoff_time:
                sent_key = self.get_deduplication_key(sent_message)
                if current_key == sent_key:
                    return False
        
        return True
    
    def get_deduplication_key(self, message: NotificationMessage) -> str:
        """
        Generate a deduplication key based on content hash and recipient
        
        Args:
            message: The message to generate key for
            
        Returns:
            str: Deduplication key (SHA256 hash)
        """
        # Create a string that uniquely identifies this message
        key_components = [
            message.content.strip(),
            message.recipient.lower(),
            message.channel.lower(),
            message.template.lower()
        ]
        
        key_string = "|".join(key_components)
        
        # Generate SHA256 hash
        return hashlib.sha256(key_string.encode('utf-8')).hexdigest()
    
    def add_sent_message(self, message: NotificationMessage) -> None:
        """
        Add a message to the sent messages cache
        
        Args:
            message: The message that was sent
        """
        key = self.get_deduplication_key(message)
        
        if key not in self.sent_messages_cache:
            self.sent_messages_cache[key] = []
        
        self.sent_messages_cache[key].append(message)
        
        # Clean up old messages
        self._cleanup_old_messages()
    
    def _cleanup_old_messages(self) -> None:
        """Remove messages older than the time window"""
        cutoff_time = datetime.now() - timedelta(hours=self.time_window_hours)
        
        for key in list(self.sent_messages_cache.keys()):
            messages = self.sent_messages_cache[key]
            
            # Filter out old messages
            recent_messages = [
                msg for msg in messages 
                if msg.timestamp >= cutoff_time
            ]
            
            if recent_messages:
                self.sent_messages_cache[key] = recent_messages
            else:
                # Remove the key if no recent messages
                del self.sent_messages_cache[key]
    
    def get_sent_messages(self, key: str) -> List[NotificationMessage]:
        """
        Get sent messages for a specific key
        
        Args:
            key: Deduplication key
            
        Returns:
            List[NotificationMessage]: List of sent messages with this key
        """
        return self.sent_messages_cache.get(key, [])
    
    def get_all_sent_messages(self) -> List[NotificationMessage]:
        """
        Get all sent messages in the cache
        
        Returns:
            List[NotificationMessage]: All sent messages
        """
        all_messages = []
        for messages in self.sent_messages_cache.values():
            all_messages.extend(messages)
        return all_messages
    
    def clear_cache(self) -> None:
        """Clear the sent messages cache"""
        self.sent_messages_cache.clear()
    
    def cache_size(self) -> int:
        """Get the current cache size"""
        return sum(len(messages) for messages in self.sent_messages_cache.values())
    
    def get_duplicate_count(self, message: NotificationMessage) -> int:
        """
        Get the number of times this message has been sent
        
        Args:
            message: The message to check
            
        Returns:
            int: Number of times this message has been sent
        """
        key = self.get_deduplication_key(message)
        return len(self.sent_messages_cache.get(key, []))
