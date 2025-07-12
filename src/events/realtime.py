"""
Real-time event source implementation
"""

from typing import List, Dict, Any, Optional
from src.events.base import EventSource
from src.core.models import NotificationEvent, EventSourceError


class RealtimeEventSource(EventSource):
    """Event source for processing real-time events from data structures"""
    
    def __init__(self):
        """Initialize the real-time event source"""
        self.events_buffer: List[Dict[str, Any]] = []
    
    @property
    def source_name(self) -> str:
        return "realtime"
    
    def get_events(self, **kwargs) -> List[NotificationEvent]:
        """
        Get events from the buffer
        
        Args:
            **kwargs: Optional parameters:
                - event_type: Filter by event type
                - limit: Maximum number of events to return
                - clear_buffer: Whether to clear the buffer after reading
                
        Returns:
            List[NotificationEvent]: List of events
            
        Raises:
            EventSourceError: If event retrieval fails
        """
        try:
            event_type = kwargs.get('event_type')
            limit = kwargs.get('limit')
            clear_buffer = kwargs.get('clear_buffer', False)
            
            # Get events from buffer
            events_data = self.events_buffer.copy()
            
            # Filter by event type if specified
            if event_type:
                events_data = [e for e in events_data if e.get('event_type') == event_type]
            
            # Apply limit if specified
            if limit and limit > 0:
                events_data = events_data[:limit]
            
            # Convert to NotificationEvent objects
            events = []
            for event_data in events_data:
                if self.validate_event_data(event_data):
                    event = self.create_event(
                        event_type=event_data.get('event_type', 'unknown'),
                        data=event_data.get('data', {}),
                        event_id=event_data.get('event_id')
                    )
                    events.append(event)
            
            # Clear buffer if requested
            if clear_buffer:
                self.events_buffer.clear()
            
            return events
            
        except Exception as e:
            raise EventSourceError(f"Failed to get real-time events: {str(e)}")
    
    def add_event(self, event_type: str, data: Dict[str, Any], 
                  event_id: Optional[str] = None) -> None:
        """
        Add an event to the buffer
        
        Args:
            event_type: Type of the event
            data: Event data
            event_id: Optional event ID
        """
        event_data = {
            'event_type': event_type,
            'data': data,
            'event_id': event_id
        }
        self.events_buffer.append(event_data)
    
    def add_events(self, events: List[Dict[str, Any]]) -> None:
        """
        Add multiple events to the buffer
        
        Args:
            events: List of event dictionaries
        """
        for event in events:
            if isinstance(event, dict):
                event_type = event.get('event_type', 'unknown')
                data = event.get('data', event)  # Use entire dict if no 'data' key
                event_id = event.get('event_id')
                self.add_event(event_type, data, event_id)
    
    def clear_buffer(self) -> None:
        """Clear the events buffer"""
        self.events_buffer.clear()
    
    def buffer_size(self) -> int:
        """Get the current buffer size"""
        return len(self.events_buffer)
    
    def validate_event_data(self, event_data: Dict[str, Any]) -> bool:
        """
        Validate if event data is valid for real-time processing
        
        Args:
            event_data: The event data to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        return (
            isinstance(event_data, dict) and
            'event_type' in event_data and
            isinstance(event_data.get('data'), dict)
        )
