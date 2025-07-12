"""
Scheduled event source implementation
"""

from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from src.events.base import EventSource
from src.core.models import NotificationEvent, EventSourceError


class ScheduledEventSource(EventSource):
    """Event source for scheduled events based on SQL queries (mocked)"""
    
    def __init__(self):
        """Initialize the scheduled event source"""
        self.queries: Dict[str, Dict[str, Any]] = {}
        self.mock_data: Dict[str, List[Dict[str, Any]]] = {}
    
    @property
    def source_name(self) -> str:
        return "scheduled"
    
    def get_events(self, **kwargs) -> List[NotificationEvent]:
        """
        Get events from scheduled queries
        
        Args:
            **kwargs: Optional parameters:
                - query_name: Specific query to execute
                - event_type: Filter by event type
                - params: Parameters for query execution
                
        Returns:
            List[NotificationEvent]: List of events
            
        Raises:
            EventSourceError: If event retrieval fails
        """
        try:
            query_name = kwargs.get('query_name')
            event_type = kwargs.get('event_type')
            params = kwargs.get('params', {})
            
            events = []
            
            # If specific query is requested
            if query_name:
                if query_name in self.queries:
                    query_events = self._execute_query(query_name, params)
                    events.extend(query_events)
            else:
                # Execute all queries
                for name in self.queries:
                    query_events = self._execute_query(name, params)
                    events.extend(query_events)
            
            # Filter by event type if specified
            if event_type:
                events = [e for e in events if e.event_type == event_type]
            
            return events
            
        except Exception as e:
            raise EventSourceError(f"Failed to get scheduled events: {str(e)}")
    
    def register_query(self, name: str, query: str, event_type: str, 
                      schedule: str = "daily", params: Optional[Dict[str, Any]] = None) -> None:
        """
        Register a scheduled query
        
        Args:
            name: Name of the query
            query: SQL query string (mocked)
            event_type: Type of events this query generates
            schedule: Schedule string (e.g., 'daily', 'hourly')
            params: Default parameters for the query
        """
        self.queries[name] = {
            'query': query,
            'event_type': event_type,
            'schedule': schedule,
            'params': params or {},
            'last_run': None
        }
    
    def set_mock_data(self, query_name: str, data: List[Dict[str, Any]]) -> None:
        """
        Set mock data for a query (for testing/demo purposes)
        
        Args:
            query_name: Name of the query
            data: Mock data to return
        """
        self.mock_data[query_name] = data
    
    def _execute_query(self, query_name: str, params: Dict[str, Any]) -> List[NotificationEvent]:
        """
        Execute a scheduled query (mocked implementation)
        
        Args:
            query_name: Name of the query to execute
            params: Parameters for query execution
            
        Returns:
            List[NotificationEvent]: List of events from query results
        """
        if query_name not in self.queries:
            return []
        
        query_config = self.queries[query_name]
        
        # Check if it's time to run (simple implementation)
        if not self._should_run_query(query_name):
            return []
        
        # Get mock data or execute actual query
        if query_name in self.mock_data:
            results = self.mock_data[query_name]
        else:
            results = self._mock_query_execution(query_config['query'], params)
        
        # Convert results to events
        events = []
        for result in results:
            event = self.create_event(
                event_type=query_config['event_type'],
                data=result,
                event_id=f"{query_name}_{result.get('id', datetime.now().timestamp())}"
            )
            events.append(event)
        
        # Update last run time
        self.queries[query_name]['last_run'] = datetime.now()
        
        return events
    
    def _should_run_query(self, query_name: str) -> bool:
        """
        Check if a query should be run based on its schedule
        
        Args:
            query_name: Name of the query
            
        Returns:
            bool: True if query should run, False otherwise
        """
        query_config = self.queries[query_name]
        last_run = query_config['last_run']
        
        if last_run is None:
            return True
        
        schedule = query_config['schedule']
        now = datetime.now()
        
        if schedule == 'daily':
            return now - last_run >= timedelta(days=1)
        elif schedule == 'hourly':
            return now - last_run >= timedelta(hours=1)
        elif schedule == 'weekly':
            return now - last_run >= timedelta(weeks=1)
        else:
            return True  # Default to always run
    
    def _mock_query_execution(self, query: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Mock SQL query execution
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List[Dict[str, Any]]: Mock query results
        """
        # This is a mock implementation - in real scenario, you'd execute the actual SQL
        
        # Example: Daily stats query
        if "daily_stats" in query.lower():
            return [
                {
                    'id': 1,
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'total_users': 1250,
                    'new_signups': 45,
                    'active_sessions': 320,
                    'revenue': 15680.50
                }
            ]
        
        # Example: User activity query
        elif "user_activity" in query.lower():
            return [
                {
                    'id': 1,
                    'user_id': 12345,
                    'user_email': 'admin@example.com',
                    'last_activity': datetime.now().isoformat(),
                    'session_count': 8
                }
            ]
        
        # Default empty result
        return []
    
    def get_query_info(self, query_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a registered query
        
        Args:
            query_name: Name of the query
            
        Returns:
            Optional[Dict[str, Any]]: Query information or None if not found
        """
        return self.queries.get(query_name)
    
    def list_queries(self) -> List[str]:
        """
        List all registered query names
        
        Returns:
            List[str]: List of query names
        """
        return list(self.queries.keys())
