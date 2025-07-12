# Notification Service

A flexible and extensible notification service built with Python, demonstrating modern OOP principles and system design.

## Features

- **Multiple Notification Channels**: Email (file-based), Slack (console-based), easily extensible
- **Templating**: Jinja2-based templating with variable substitution
- **Event Sources**: Real-time and scheduled event processing
- **Notification Registry**: Centralized configuration management
- **Deduplication**: Configurable deduplication policies
- **Modern Python**: Type hints, dataclasses, dependency injection

## Project Structure

```
notification_service/
├── src/
│   ├── __init__.py
│   ├── channels/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── email.py
│   │   └── slack.py
│   ├── templates/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── jinja2_engine.py
│   ├── events/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── realtime.py
│   │   └── scheduled.py
│   ├── registry/
│   │   ├── __init__.py
│   │   └── notification_registry.py
│   ├── deduplication/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── content_based.py
│   └── core/
│       ├── __init__.py
│       ├── container.py
│       └── models.py
├── templates/
│   ├── welcome_email.txt
│   ├── daily_stats.txt
│   └── slack_welcome.txt
├── examples/
│   └── usage_examples.py
├── tests/
│   └── test_notification_service.py
├── requirements.txt
└── README.md
```

## Quick Start

```python
from src.core.container import Container
from src.registry.notification_registry import NotificationRegistry

# Initialize the container
container = Container()

# Get the notification registry
registry = container.get(NotificationRegistry)

# Process events
registry.process_event('user_signup', {'user_email': 'user@example.com', 'user_name': 'John Doe'})
```

## Adding New Channels

To add a new notification channel:

1. Create a new class inheriting from `NotificationChannel`
2. Implement the `send` method
3. Register it in the container

```python
from src.channels.base import NotificationChannel

class SMSChannel(NotificationChannel):
    def send(self, message: str, recipient: str, **kwargs) -> bool:
        # Implementation here
        pass
```

## Adding New Templates

Templates are stored in the `templates/` directory and use Jinja2 syntax.

## Adding New Event Sources

Create a new class inheriting from `EventSource` and implement the `get_events` method.

## Configuration

All notifications are configured in `examples/usage_examples.py` and can be easily viewed and modified.
