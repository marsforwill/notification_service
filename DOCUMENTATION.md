# Notification Service Documentation

## Architecture Overview

The notification service is built using clean OOP principles with proper abstractions and dependency injection. The system is designed to be highly extensible and maintainable.

### Core Components

1. **Channels** (`src/channels/`) - Handle different notification delivery methods
2. **Templates** (`src/templates/`) - Handle message templating and rendering
3. **Events** (`src/events/`) - Handle different event sources
4. **Deduplication** (`src/deduplication/`) - Prevent duplicate notifications
5. **Registry** (`src/registry/`) - Manage notification configurations
6. **Core** (`src/core/`) - Data models and dependency injection

## Key Features

### 1. Multiple Notification Channels
- **Email**: Writes to files (mock implementation)
- **Slack**: Prints to console (mock implementation)
- **Extensible**: Easy to add new channels

### 2. Templating System
- **Jinja2**: Full Jinja2 templating support
- **Variable Substitution**: Dynamic content from event data
- **File-based Templates**: Store templates in files

### 3. Event Sources
- **Real-time**: Process lists of dictionaries as events
- **Scheduled**: Execute SQL queries (mocked with sample data)
- **Parameterized**: Support for query parameters

### 4. Deduplication
- **Content-based**: Prevents duplicate messages based on content hash
- **Time-window**: Configurable time window for duplicate detection
- **Extensible**: Easy to add new deduplication policies

### 5. Dependency Injection
- **Container**: Manages service dependencies
- **Testable**: Easy to mock dependencies for testing
- **Configurable**: Services can be replaced or customized

## How to Add New Components

### Adding a New Notification Channel

1. Create a new class inheriting from `NotificationChannel`:

```python
from src.channels.base import NotificationChannel
from src.core.models import NotificationResult, ChannelError

class SMSChannel(NotificationChannel):
    @property
    def channel_name(self) -> str:
        return "sms"
    
    def validate_recipient(self, recipient: str) -> bool:
        # Validate phone number format
        return bool(recipient and recipient.startswith("+"))
    
    def send(self, message: str, recipient: str, **kwargs) -> NotificationResult:
        try:
            # Implement SMS sending logic here
            # For mock implementation, you could write to a file or print
            print(f"SMS to {recipient}: {message}")
            
            return NotificationResult(
                success=True,
                message=f"SMS sent to {recipient}",
                channel=self.channel_name,
                recipient=recipient
            )
        except Exception as e:
            return NotificationResult(
                success=False,
                message=f"Failed to send SMS: {str(e)}",
                channel=self.channel_name,
                recipient=recipient,
                error=str(e)
            )
```

2. Register the channel in the container:

```python
from src.core.container import Container

container = Container()
container.register_factory(SMSChannel, SMSChannel)
```

3. Update the registry to support the new channel:

```python
# In NotificationRegistry._get_channel method
if channel_name.lower() == "sms":
    return self.container.get(SMSChannel)
```

### Adding a New Template Engine

1. Create a new class inheriting from `TemplateEngine`:

```python
from src.templates.base import TemplateEngine
from src.core.models import TemplateError

class CustomTemplateEngine(TemplateEngine):
    def render(self, template_name: str, variables: Dict[str, Any]) -> str:
        # Implement custom template rendering logic
        pass
    
    def load_template(self, template_name: str) -> str:
        # Implement template loading logic
        pass
```

2. Register in the container:

```python
container.register_factory(CustomTemplateEngine, CustomTemplateEngine)
```

### Adding a New Event Source

1. Create a new class inheriting from `EventSource`:

```python
from src.events.base import EventSource
from src.core.models import NotificationEvent, EventSourceError

class WebhookEventSource(EventSource):
    @property
    def source_name(self) -> str:
        return "webhook"
    
    def get_events(self, **kwargs) -> List[NotificationEvent]:
        # Implement webhook event retrieval logic
        pass
```

2. Register in the container:

```python
container.register_factory(WebhookEventSource, WebhookEventSource)
```

### Adding a New Deduplication Policy

1. Create a new class inheriting from `DeduplicationPolicy`:

```python
from src.deduplication.base import DeduplicationPolicy
from src.core.models import NotificationMessage

class TimeBasedDeduplicationPolicy(DeduplicationPolicy):
    @property
    def policy_name(self) -> str:
        return "time_based"
    
    def should_send(self, message: NotificationMessage, 
                   sent_messages: List[NotificationMessage]) -> bool:
        # Implement time-based deduplication logic
        pass
    
    def get_deduplication_key(self, message: NotificationMessage) -> str:
        # Generate time-based deduplication key
        pass
```

2. Register in the container:

```python
container.register_factory(TimeBasedDeduplicationPolicy, TimeBasedDeduplicationPolicy)
```

## Configuration Examples

### Basic Notification Configuration

```python
from src.core.models import NotificationConfig

# Email notification for user signups
config = NotificationConfig(
    event_type="user_signup",
    channel="email",
    template="welcome_email.txt",
    recipient_field="user_email",
    deduplication_policy="content_based",
    metadata={
        "subject": "Welcome to our platform!",
        "from_email": "welcome@company.com"
    }
)
```

### Multiple Channel Configuration

```python
# Email + Slack notification for the same event
email_config = NotificationConfig(
    event_type="user_signup",
    channel="email",
    template="welcome_email.txt",
    recipient_field="user_email"
)

slack_config = NotificationConfig(
    event_type="user_signup",
    channel="slack",
    template="slack_welcome.txt",
    recipient_field="slack_channel"
)

registry.register_notifications([email_config, slack_config])
```

### Processing Events

```python
# Process a single event
registry.process_event("user_signup", {
    "user_name": "John Doe",
    "user_email": "john@example.com",
    "slack_channel": "#new-users"
})

# Process multiple events
events = [
    NotificationEvent("user_signup", {"user_name": "Alice", "user_email": "alice@example.com"}),
    NotificationEvent("user_signup", {"user_name": "Bob", "user_email": "bob@example.com"})
]
registry.process_events(events)
```

## Template Examples

### Email Template (`templates/welcome_email.txt`)

```jinja2
Welcome to our platform, {{ user_name }}! 🎉

We're excited to have you join our community. Here are your account details:

📧 Email: {{ user_email }}
📅 Registration Date: {{ registration_date }}
🆔 User ID: {{ user_id }}

Getting Started:
• Complete your profile by visiting {{ profile_url }}
• Explore our features at {{ features_url }}
• Join our community forum at {{ community_url }}

Need help? Contact our support team at {{ support_email }}

Best regards,
The {{ company_name }} Team
```

### Slack Template (`templates/slack_welcome.txt`)

```jinja2
🎉 Welcome {{ user_name }} to our platform! 

New user just signed up:
• Email: {{ user_email }}
• Registration Date: {{ registration_date }}
• User ID: {{ user_id }}

Let's make them feel welcome! 🚀
```

## Testing

### Running Tests

```bash
# Run all tests
python -m unittest tests.test_notification_service

# Run specific test
python -m unittest tests.test_notification_service.TestNotificationService.test_email_channel_send

# Run with verbose output
python -m unittest tests.test_notification_service -v
```

### Writing Tests

```python
import unittest
from src.channels.email import EmailChannel

class TestCustomChannel(unittest.TestCase):
    def test_send_message(self):
        channel = EmailChannel()
        result = channel.send("Test message", "test@example.com")
        self.assertTrue(result.success)
```

## Best Practices

### 1. Error Handling
- Always return `NotificationResult` objects with proper error information
- Use specific exception types (`ChannelError`, `TemplateError`, etc.)
- Log errors appropriately

### 2. Configuration Management
- Store configuration in centralized locations
- Use environment variables for sensitive data
- Validate configuration on startup

### 3. Template Management
- Use descriptive template names
- Organize templates by channel or event type
- Include fallback templates for error cases

### 4. Performance Considerations
- Implement connection pooling for external services
- Use async operations for I/O-bound tasks
- Cache templates and configurations

### 5. Security
- Validate all input data
- Sanitize template variables
- Use secure connections for external services
- Implement rate limiting

## Deployment Considerations

### 1. Environment Setup
- Install dependencies: `pip install -r requirements.txt`
- Set up template directories
- Configure output directories for file-based channels

### 2. Configuration
- Set up environment-specific templates
- Configure deduplication policies
- Set up monitoring and logging

### 3. Scaling
- Use message queues for high-volume scenarios
- Implement horizontal scaling for processing
- Use database-backed deduplication for distributed systems

### 4. Monitoring
- Track notification success/failure rates
- Monitor template rendering performance
- Set up alerts for high error rates

## Advanced Features

### 1. Conditional Notifications
```python
# Only send if certain conditions are met
if event.data.get("user_type") == "premium":
    registry.process_event("premium_signup", event.data)
```

### 2. Scheduled Notifications
```python
# Set up recurring notifications
scheduled_source = ScheduledEventSource()
scheduled_source.register_query(
    name="daily_report",
    query="SELECT * FROM daily_stats",
    event_type="daily_report",
    schedule="daily"
)
```

### 3. Notification Chains
```python
# Chain multiple notifications
def process_user_signup(user_data):
    # Send welcome email
    registry.process_event("user_signup", user_data)
    
    # Schedule follow-up email
    followup_data = user_data.copy()
    followup_data["send_date"] = datetime.now() + timedelta(days=1)
    registry.process_event("followup_email", followup_data)
```

This documentation provides a comprehensive guide for understanding, extending, and maintaining the notification service. The system is designed to be flexible and extensible while maintaining clean code and proper architectural patterns.
