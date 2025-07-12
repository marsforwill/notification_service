"""
Channel implementations
"""

from .base import NotificationChannel
from .email import EmailChannel
from .slack import SlackChannel

__all__ = ['NotificationChannel', 'EmailChannel', 'SlackChannel']
