"""
Example usage of the notification service

This file demonstrates how to use the notification service for various scenarios.
"""

from datetime import datetime
from src.core.container import Container
from src.core.models import NotificationConfig
from src.registry.notification_registry import NotificationRegistry
from src.events.realtime import RealtimeEventSource
from src.events.scheduled import ScheduledEventSource


def setup_example_notifications(container: Container) -> NotificationRegistry:
    """
    Set up example notification configurations
    
    Args:
        container: Dependency injection container
        
    Returns:
        NotificationRegistry: Configured notification registry
    """
    registry = container.get(NotificationRegistry)
    
    # Configuration for user signup notifications
    user_signup_email = NotificationConfig(
        event_type="user_signup",
        channel="email",
        template="welcome_email.txt",
        recipient_field="user_email",
        deduplication_policy="content_based",
        metadata={
            "subject": "Welcome to our platform!",
            "from_email": "welcome@mycompany.com"
        }
    )
    
    user_signup_slack = NotificationConfig(
        event_type="user_signup",
        channel="slack",
        template="slack_welcome.txt",
        recipient_field="slack_channel",
        deduplication_policy="content_based",
        metadata={
            "username": "Welcome Bot",
            "icon_emoji": ":wave:"
        }
    )
    
    # Configuration for daily stats report
    daily_stats_email = NotificationConfig(
        event_type="daily_stats",
        channel="email",
        template="daily_stats.txt",
        recipient_field="admin_email",
        deduplication_policy="content_based",
        metadata={
            "subject": "Daily Statistics Report",
            "from_email": "reports@mycompany.com"
        }
    )
    
    # Register all configurations
    registry.register_notifications([
        user_signup_email,
        user_signup_slack,
        daily_stats_email
    ])
    
    return registry


def example_user_signup_notification():
    """Example: User signup notification"""
    print("🔔 Example: User Signup Notification")
    print("=" * 50)
    
    # Initialize container and registry
    container = Container()
    registry = setup_example_notifications(container)
    
    # Simulate user signup event
    signup_data = {
        "user_name": "John Doe",
        "user_email": "john.doe@example.com",
        "user_id": "12345",
        "registration_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "profile_url": "https://mycompany.com/profile",
        "features_url": "https://mycompany.com/features",
        "community_url": "https://mycompany.com/community",
        "support_email": "support@mycompany.com",
        "company_name": "MyCompany",
        "slack_channel": "#new-users"
    }
    
    # Process the event
    results = registry.process_event("user_signup", signup_data, event_id="signup_001")
    
    # Display results
    for result in results:
        print(f"Channel: {result.channel}")
        print(f"Recipient: {result.recipient}")
        print(f"Success: {result.success}")
        print(f"Message: {result.message}")
        if result.error:
            print(f"Error: {result.error}")
        print("-" * 30)
    
    print()


def example_daily_stats_notification():
    """Example: Daily stats notification"""
    print("📊 Example: Daily Stats Notification")
    print("=" * 50)
    
    # Initialize container and registry
    container = Container()
    registry = setup_example_notifications(container)
    
    # Simulate daily stats event
    stats_data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "total_users": 1250,
        "new_signups": 45,
        "active_sessions": 320,
        "revenue": 15680.50,
        "daily_growth": "12.5%",
        "success_rate": "99.2%",
        "avg_response_time": "245ms",
        "top_events": [
            {"name": "User Login", "count": 1250},
            {"name": "Page View", "count": 5680},
            {"name": "Purchase", "count": 89}
        ],
        "generation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "admin_email": "admin@mycompany.com"
    }
    
    # Process the event
    results = registry.process_event("daily_stats", stats_data, event_id="stats_001")
    
    # Display results
    for result in results:
        print(f"Channel: {result.channel}")
        print(f"Recipient: {result.recipient}")
        print(f"Success: {result.success}")
        print(f"Message: {result.message}")
        if result.error:
            print(f"Error: {result.error}")
        print("-" * 30)
    
    print()


def example_realtime_events():
    """Example: Processing real-time events"""
    print("⚡ Example: Real-time Events Processing")
    print("=" * 50)
    
    # Initialize container and registry
    container = Container()
    registry = setup_example_notifications(container)
    realtime_source = container.get(RealtimeEventSource)
    
    # Add multiple events to the realtime source
    events_data = [
        {
            "event_type": "user_signup",
            "data": {
                "user_name": "Alice Smith",
                "user_email": "alice@example.com",
                "user_id": "12346",
                "registration_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "profile_url": "https://mycompany.com/profile",
                "features_url": "https://mycompany.com/features",
                "community_url": "https://mycompany.com/community",
                "support_email": "support@mycompany.com",
                "company_name": "MyCompany",
                "slack_channel": "#new-users"
            }
        },
        {
            "event_type": "user_signup",
            "data": {
                "user_name": "Bob Johnson",
                "user_email": "bob@example.com",
                "user_id": "12347",
                "registration_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "profile_url": "https://mycompany.com/profile",
                "features_url": "https://mycompany.com/features",
                "community_url": "https://mycompany.com/community",
                "support_email": "support@mycompany.com",
                "company_name": "MyCompany",
                "slack_channel": "#new-users"
            }
        }
    ]
    
    # Add events to the realtime source
    realtime_source.add_events(events_data)
    
    # Get events from the source
    events = realtime_source.get_events(clear_buffer=True)
    
    # Process all events
    all_results = registry.process_events(events)
    
    # Display results
    for result in all_results:
        print(f"Channel: {result.channel}")
        print(f"Recipient: {result.recipient}")
        print(f"Success: {result.success}")
        print(f"Message: {result.message}")
        if result.error:
            print(f"Error: {result.error}")
        print("-" * 30)
    
    print()


def example_scheduled_events():
    """Example: Processing scheduled events"""
    print("⏰ Example: Scheduled Events Processing")
    print("=" * 50)
    
    # Initialize container and registry
    container = Container()
    registry = setup_example_notifications(container)
    scheduled_source = container.get(ScheduledEventSource)
    
    # Register a scheduled query
    scheduled_source.register_query(
        name="daily_stats_query",
        query="SELECT * FROM daily_stats WHERE date = CURRENT_DATE",
        event_type="daily_stats",
        schedule="daily"
    )
    
    # Set mock data for the query
    mock_stats = [
        {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_users": 1500,
            "new_signups": 65,
            "active_sessions": 420,
            "revenue": 18750.75,
            "daily_growth": "15.8%",
            "success_rate": "99.5%",
            "avg_response_time": "230ms",
            "top_events": [
                {"name": "User Login", "count": 1500},
                {"name": "Page View", "count": 6200},
                {"name": "Purchase", "count": 125}
            ],
            "generation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "admin_email": "admin@mycompany.com"
        }
    ]
    
    scheduled_source.set_mock_data("daily_stats_query", mock_stats)
    
    # Get events from the scheduled source
    events = scheduled_source.get_events(query_name="daily_stats_query")
    
    # Process events
    results = registry.process_events(events)
    
    # Display results
    for result in results:
        print(f"Channel: {result.channel}")
        print(f"Recipient: {result.recipient}")
        print(f"Success: {result.success}")
        print(f"Message: {result.message}")
        if result.error:
            print(f"Error: {result.error}")
        print("-" * 30)
    
    print()


def example_deduplication():
    """Example: Deduplication in action"""
    print("🔄 Example: Deduplication Policy")
    print("=" * 50)
    
    # Initialize container and registry
    container = Container()
    registry = setup_example_notifications(container)
    
    # Same event data - should trigger deduplication
    duplicate_data = {
        "user_name": "Jane Doe",
        "user_email": "jane@example.com",
        "user_id": "12348",
        "registration_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "profile_url": "https://mycompany.com/profile",
        "features_url": "https://mycompany.com/features",
        "community_url": "https://mycompany.com/community",
        "support_email": "support@mycompany.com",
        "company_name": "MyCompany",
        "slack_channel": "#new-users"
    }
    
    # Send first notification
    print("Sending first notification...")
    results1 = registry.process_event("user_signup", duplicate_data, event_id="dup_001")
    for result in results1:
        print(f"  {result.channel}: {result.success} - {result.message}")
    
    print("\nSending duplicate notification...")
    # Send the same notification again - should be deduplicated
    results2 = registry.process_event("user_signup", duplicate_data, event_id="dup_002")
    for result in results2:
        print(f"  {result.channel}: {result.success} - {result.message}")
    
    print()


def print_registry_summary():
    """Print a summary of the notification registry"""
    print("📋 Notification Registry Summary")
    print("=" * 50)
    
    # Initialize container and registry
    container = Container()
    registry = setup_example_notifications(container)
    
    # Print the summary
    registry.print_notification_summary()


def main():
    """Main function to run all examples"""
    print("🚀 Notification Service Examples")
    print("=" * 80)
    print()
    
    # Run examples
    example_user_signup_notification()
    example_daily_stats_notification()
    example_realtime_events()
    example_scheduled_events()
    example_deduplication()
    print_registry_summary()
    
    print("✅ All examples completed!")


if __name__ == "__main__":
    main()
