"""
Base event source interface
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from src.core.models import NotificationEvent, EventSourceError


class EventSource(ABC):
    """Abstract base class for event sources"""
    
    @abstractmethod
    def get_events(self, **kwargs) -> List[NotificationEvent]:
        """
        Get events from this source
        
        Args:
            **kwargs: Source-specific parameters
            
        Returns:
            List[NotificationEvent]: List of events
            
        Raises:
            EventSourceError: If event retrieval fails
        """
        pass
    
    @property
    @abstractmethod
    def source_name(self) -> str:
        """Return the name of this event source"""
        pass
    
    def validate_event_data(self, event_data: Dict[str, Any]) -> bool:
        """
        Validate if event data is valid
        
        Args:
            event_data: The event data to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        return bool(event_data)
    
    def create_event(self, event_type: str, data: Dict[str, Any], 
                    event_id: Optional[str] = None) -> NotificationEvent:
        """
        Create a NotificationEvent from raw data
        
        Args:
            event_type: Type of the event
            data: Event data
            event_id: Optional event ID
            
        Returns:
            NotificationEvent: Created event
        """
        return NotificationEvent(
            event_type=event_type,
            data=data,
            event_id=event_id,
            source=self.source_name
        )
    
    def filter_events(self, events: List[NotificationEvent], 
                     filters: Dict[str, Any]) -> List[NotificationEvent]:
        """
        Filter events based on criteria
        
        Args:
            events: List of events to filter
            filters: Filter criteria
            
        Returns:
            List[NotificationEvent]: Filtered events
        """
        if not filters:
            return events
        
        filtered_events = []
        for event in events:
            if self._matches_filters(event, filters):
                filtered_events.append(event)
        
        return filtered_events
    
    def _matches_filters(self, event: NotificationEvent, filters: Dict[str, Any]) -> bool:
        """Check if an event matches the given filters"""
        for key, value in filters.items():
            if key == 'event_type':
                if event.event_type != value:
                    return False
            elif key in event.data:
                if event.data[key] != value:
                    return False
        return True
