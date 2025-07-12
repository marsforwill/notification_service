"""
Core data models and types for the notification service
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime


@dataclass
class NotificationEvent:
    """Represents a notification event with metadata"""
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    event_id: Optional[str] = None
    source: str = "unknown"


@dataclass
class NotificationMessage:
    """Represents a formatted notification message"""
    content: str
    recipient: str
    channel: str
    template: str
    event_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class NotificationResult:
    """Represents the result of a notification attempt"""
    success: bool
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    channel: str = ""
    recipient: str = ""
    error: Optional[str] = None


@dataclass
class NotificationConfig:
    """Configuration for a notification"""
    event_type: str
    channel: str
    template: str
    recipient_field: str
    event_source: Optional[str] = None
    deduplication_policy: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class NotificationError(Exception):
    """Base exception for notification-related errors"""
    pass


class TemplateError(NotificationError):
    """Exception for template-related errors"""
    pass


class ChannelError(NotificationError):
    """Exception for channel-related errors"""
    pass


class EventSourceError(NotificationError):
    """Exception for event source-related errors"""
    pass
