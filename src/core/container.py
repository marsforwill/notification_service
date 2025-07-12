"""
Dependency injection container for the notification service
"""

from typing import Dict, Type, TypeVar, Any, Optional
from abc import ABC, abstractmethod
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


T = TypeVar('T')


class DIContainer:
    """Simple dependency injection container"""
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, callable] = {}
    
    def register(self, interface: Type[T], implementation: T) -> None:
        """Register a service instance"""
        self._services[interface] = implementation
    
    def register_factory(self, interface: Type[T], factory: callable) -> None:
        """Register a factory function for creating service instances"""
        self._factories[interface] = factory
    
    def get(self, interface: Type[T]) -> T:
        """Get a service instance"""
        if interface in self._services:
            return self._services[interface]
        
        if interface in self._factories:
            instance = self._factories[interface]()
            self._services[interface] = instance
            return instance
        
        raise ValueError(f"Service {interface} not registered")
    
    def get_optional(self, interface: Type[T]) -> Optional[T]:
        """Get a service instance if registered, otherwise return None"""
        try:
            return self.get(interface)
        except ValueError:
            return None


class Container:
    """Main container for the notification service"""
    
    def __init__(self):
        self._container = DIContainer()
        self._setup_default_services()
    
    def _setup_default_services(self):
        """Setup default services"""
        # Import here to avoid circular imports
        from channels.email import EmailChannel
        from channels.slack import SlackChannel
        from templates.jinja2_engine import Jinja2TemplateEngine
        from events.realtime import RealtimeEventSource
        from events.scheduled import ScheduledEventSource
        from deduplication.content_based import ContentBasedDeduplicationPolicy
        from registry.notification_registry import NotificationRegistry
        
        # Register channels
        self._container.register_factory(EmailChannel, EmailChannel)
        self._container.register_factory(SlackChannel, SlackChannel)
        
        # Register template engine
        self._container.register_factory(Jinja2TemplateEngine, Jinja2TemplateEngine)
        
        # Register event sources
        self._container.register_factory(RealtimeEventSource, RealtimeEventSource)
        self._container.register_factory(ScheduledEventSource, ScheduledEventSource)
        
        # Register deduplication policy
        self._container.register_factory(ContentBasedDeduplicationPolicy, ContentBasedDeduplicationPolicy)
        
        # Register notification registry
        self._container.register_factory(NotificationRegistry, lambda: NotificationRegistry(self))
    
    def get(self, interface: Type[T]) -> T:
        """Get a service instance"""
        return self._container.get(interface)
    
    def get_optional(self, interface: Type[T]) -> Optional[T]:
        """Get a service instance if registered, otherwise return None"""
        return self._container.get_optional(interface)
    
    def register(self, interface: Type[T], implementation: T) -> None:
        """Register a service instance"""
        self._container.register(interface, implementation)
    
    def register_factory(self, interface: Type[T], factory: callable) -> None:
        """Register a factory function for creating service instances"""
        self._container.register_factory(interface, factory)
