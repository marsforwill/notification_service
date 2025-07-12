"""
Notification registry for managing all notification configurations
"""

from typing import Dict, List, Any, Optional, TYPE_CHECKING
from src.core.models import (
    NotificationConfig, NotificationEvent, NotificationMessage, 
    NotificationResult, NotificationError
)
from src.channels.base import NotificationChannel
from src.templates.base import TemplateEngine
from src.events.base import EventSource
from src.deduplication.base import DeduplicationPolicy

if TYPE_CHECKING:
    from src.core.container import Container


class NotificationRegistry:
    """Registry for managing notification configurations and processing"""
    
    def __init__(self, container: 'Container'):
        """
        Initialize the notification registry
        
        Args:
            container: Dependency injection container
        """
        self.container = container
        self.configurations: Dict[str, NotificationConfig] = {}
        self.sent_messages: List[NotificationMessage] = []
    
    def register_notification(self, config: NotificationConfig) -> None:
        """
        Register a notification configuration
        
        Args:
            config: The notification configuration to register
        """
        key = f"{config.event_type}_{config.channel}"
        self.configurations[key] = config
    
    def register_notifications(self, configs: List[NotificationConfig]) -> None:
        """
        Register multiple notification configurations
        
        Args:
            configs: List of notification configurations to register
        """
        for config in configs:
            self.register_notification(config)
    
    def get_configurations(self, event_type: str = None) -> List[NotificationConfig]:
        """
        Get notification configurations, optionally filtered by event type
        
        Args:
            event_type: Optional event type to filter by
            
        Returns:
            List[NotificationConfig]: List of matching configurations
        """
        if event_type:
            return [
                config for config in self.configurations.values()
                if config.event_type == event_type
            ]
        return list(self.configurations.values())
    
    def process_event(self, event_type: str, event_data: Dict[str, Any], 
                     event_id: Optional[str] = None) -> List[NotificationResult]:
        """
        Process a single event and send notifications
        
        Args:
            event_type: Type of the event
            event_data: Event data
            event_id: Optional event ID
            
        Returns:
            List[NotificationResult]: List of notification results
        """
        event = NotificationEvent(
            event_type=event_type,
            data=event_data,
            event_id=event_id,
            source="manual"
        )
        
        return self.process_events([event])
    
    def process_events(self, events: List[NotificationEvent]) -> List[NotificationResult]:
        """
        Process multiple events and send notifications
        
        Args:
            events: List of events to process
            
        Returns:
            List[NotificationResult]: List of notification results
        """
        results = []
        
        for event in events:
            # Get matching configurations
            configs = self.get_configurations(event.event_type)
            
            for config in configs:
                try:
                    result = self._process_single_notification(event, config)
                    results.append(result)
                except Exception as e:
                    results.append(NotificationResult(
                        success=False,
                        message=f"Failed to process notification: {str(e)}",
                        channel=config.channel,
                        recipient=event.data.get(config.recipient_field, "unknown"),
                        error=str(e)
                    ))
        
        return results
    
    def _process_single_notification(self, event: NotificationEvent, 
                                   config: NotificationConfig) -> NotificationResult:
        """
        Process a single notification
        
        Args:
            event: The event to process
            config: The notification configuration
            
        Returns:
            NotificationResult: Result of the notification
        """
        # Get recipient from event data
        recipient = event.data.get(config.recipient_field)
        if not recipient:
            raise NotificationError(f"Recipient field '{config.recipient_field}' not found in event data")
        
        # Get template engine and render message
        template_engine = self.container.get(TemplateEngine)
        try:
            message_content = template_engine.render(config.template, event.data)
        except Exception as e:
            raise NotificationError(f"Failed to render template '{config.template}': {str(e)}")
        
        # Create notification message
        message = NotificationMessage(
            content=message_content,
            recipient=recipient,
            channel=config.channel,
            template=config.template,
            event_id=event.event_id,
            metadata=config.metadata
        )
        
        # Check deduplication if policy is specified
        if config.deduplication_policy:
            dedup_policy = self._get_deduplication_policy(config.deduplication_policy)
            if dedup_policy and not dedup_policy.should_send(message, self.sent_messages):
                return NotificationResult(
                    success=False,
                    message="Message skipped due to deduplication policy",
                    channel=config.channel,
                    recipient=recipient
                )
        
        # Get channel and send message
        channel = self._get_channel(config.channel)
        if not channel:
            raise NotificationError(f"Channel '{config.channel}' not found")
        
        # Send the message
        result = channel.send(
            message=message.content,
            recipient=recipient,
            **config.metadata
        )
        
        # Store sent message for deduplication
        if result.success:
            self.sent_messages.append(message)
            
            # Add to deduplication cache if policy exists
            if config.deduplication_policy:
                dedup_policy = self._get_deduplication_policy(config.deduplication_policy)
                if dedup_policy and hasattr(dedup_policy, 'add_sent_message'):
                    dedup_policy.add_sent_message(message)
        
        return result
    
    def _get_channel(self, channel_name: str) -> Optional[NotificationChannel]:
        """Get a channel by name"""
        from src.channels.email import EmailChannel
        from src.channels.slack import SlackChannel
        
        if channel_name.lower() == "email":
            return self.container.get(EmailChannel)
        elif channel_name.lower() == "slack":
            return self.container.get(SlackChannel)
        else:
            return None
    
    def _get_deduplication_policy(self, policy_name: str) -> Optional[DeduplicationPolicy]:
        """Get a deduplication policy by name"""
        from src.deduplication.content_based import ContentBasedDeduplicationPolicy
        
        if policy_name.lower() == "content_based":
            return self.container.get(ContentBasedDeduplicationPolicy)
        else:
            return None
    
    def get_notification_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all registered notifications
        
        Returns:
            Dict[str, Any]: Summary of the notification registry
        """
        summary = {
            "total_configurations": len(self.configurations),
            "configurations_by_event_type": {},
            "configurations_by_channel": {},
            "total_sent_messages": len(self.sent_messages),
            "configurations": []
        }
        
        # Group by event type
        for config in self.configurations.values():
            if config.event_type not in summary["configurations_by_event_type"]:
                summary["configurations_by_event_type"][config.event_type] = []
            summary["configurations_by_event_type"][config.event_type].append(config.channel)
        
        # Group by channel
        for config in self.configurations.values():
            if config.channel not in summary["configurations_by_channel"]:
                summary["configurations_by_channel"][config.channel] = []
            summary["configurations_by_channel"][config.channel].append(config.event_type)
        
        # Add detailed configuration info
        for config in self.configurations.values():
            summary["configurations"].append({
                "event_type": config.event_type,
                "channel": config.channel,
                "template": config.template,
                "recipient_field": config.recipient_field,
                "deduplication_policy": config.deduplication_policy,
                "metadata": config.metadata
            })
        
        return summary
    
    def print_notification_summary(self) -> None:
        """Print a formatted summary of all registered notifications"""
        summary = self.get_notification_summary()
        
        print("=" * 80)
        print("NOTIFICATION REGISTRY SUMMARY")
        print("=" * 80)
        print(f"Total Configurations: {summary['total_configurations']}")
        print(f"Total Sent Messages: {summary['total_sent_messages']}")
        print()
        
        print("CONFIGURATIONS BY EVENT TYPE:")
        print("-" * 40)
        for event_type, channels in summary["configurations_by_event_type"].items():
            print(f"  {event_type}:")
            for channel in channels:
                print(f"    → {channel}")
        print()
        
        print("CONFIGURATIONS BY CHANNEL:")
        print("-" * 40)
        for channel, event_types in summary["configurations_by_channel"].items():
            print(f"  {channel}:")
            for event_type in event_types:
                print(f"    → {event_type}")
        print()
        
        print("DETAILED CONFIGURATIONS:")
        print("-" * 40)
        for config in summary["configurations"]:
            print(f"  Event: {config['event_type']}")
            print(f"  Channel: {config['channel']}")
            print(f"  Template: {config['template']}")
            print(f"  Recipient Field: {config['recipient_field']}")
            if config['deduplication_policy']:
                print(f"  Deduplication: {config['deduplication_policy']}")
            print(f"  Metadata: {config['metadata']}")
            print()
        
        print("=" * 80)
    
    def clear_sent_messages(self) -> None:
        """Clear the sent messages history"""
        self.sent_messages.clear()
    
    def get_sent_messages_count(self) -> int:
        """Get the number of sent messages"""
        return len(self.sent_messages)
