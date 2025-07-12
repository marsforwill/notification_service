"""
Simple demonstration of the notification service
"""

import os
import sys
from datetime import datetime

# Add the current directory to the path to import from src
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Now we can import our modules
from src.core.models import NotificationConfig, NotificationEvent
from src.channels.email import EmailChannel
from src.channels.slack import SlackChannel
from src.templates.jinja2_engine import Jinja2TemplateEngine
from src.deduplication.content_based import ContentBasedDeduplicationPolicy


def demo_email_channel():
    """Demonstrate email channel functionality"""
    print("🔔 Email Channel Demo")
    print("=" * 50)
    
    # Create email channel
    email_channel = EmailChannel()
    
    # Send a test email
    result = email_channel.send(
        message="Hello John! Welcome to our amazing platform. We're excited to have you on board!",
        recipient="john.doe@example.com",
        subject="Welcome to Our Platform!",
        from_email="welcome@mycompany.com"
    )
    
    print(f"Success: {result.success}")
    print(f"Message: {result.message}")
    print(f"Channel: {result.channel}")
    print(f"Recipient: {result.recipient}")
    print()


def demo_slack_channel():
    """Demonstrate Slack channel functionality"""
    print("💬 Slack Channel Demo")
    print("=" * 50)
    
    # Create Slack channel
    slack_channel = SlackChannel()
    
    # Send a test Slack message
    result = slack_channel.send(
        message="🎉 New user John Doe just signed up! Let's welcome them to our community.",
        recipient="#new-users",
        username="Welcome Bot",
        icon_emoji=":wave:"
    )
    
    print(f"Success: {result.success}")
    print(f"Message: {result.message}")
    print(f"Channel: {result.channel}")
    print(f"Recipient: {result.recipient}")
    print()


def demo_template_engine():
    """Demonstrate template engine functionality"""
    print("📝 Template Engine Demo")
    print("=" * 50)
    
    # Create template engine
    template_engine = Jinja2TemplateEngine()
    
    # Test string template rendering
    template_string = "Hello {{ name }}! Your account ID is {{ user_id }}. Welcome to {{ company }}!"
    
    result = template_engine.render_string(template_string, {
        "name": "Alice Smith",
        "user_id": "12345",
        "company": "TechCorp"
    })
    
    print(f"Template: {template_string}")
    print(f"Rendered: {result}")
    print()


def demo_deduplication():
    """Demonstrate deduplication functionality"""
    print("🔄 Deduplication Demo")
    print("=" * 50)
    
    from src.core.models import NotificationMessage
    
    # Create deduplication policy
    dedup_policy = ContentBasedDeduplicationPolicy(time_window_hours=24)
    
    # Create identical messages
    message1 = NotificationMessage(
        content="Welcome to our platform!",
        recipient="test@example.com",
        channel="email",
        template="welcome.txt"
    )
    
    message2 = NotificationMessage(
        content="Welcome to our platform!",
        recipient="test@example.com", 
        channel="email",
        template="welcome.txt"
    )
    
    # Test deduplication
    should_send_first = dedup_policy.should_send(message1, [])
    dedup_policy.add_sent_message(message1)
    should_send_second = dedup_policy.should_send(message2, dedup_policy.get_all_sent_messages())
    
    print(f"Should send first message: {should_send_first}")
    print(f"Should send second message (duplicate): {should_send_second}")
    print(f"Deduplication key: {dedup_policy.get_deduplication_key(message1)}")
    print()


def demo_file_templates():
    """Demonstrate file-based template rendering"""
    print("📄 File Template Demo")
    print("=" * 50)
    
    template_engine = Jinja2TemplateEngine()
    
    # Try to render the welcome email template
    try:
        result = template_engine.render("welcome_email.txt", {
            "user_name": "John Doe",
            "user_email": "john.doe@example.com",
            "user_id": "12345",
            "registration_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "profile_url": "https://mycompany.com/profile",
            "features_url": "https://mycompany.com/features", 
            "community_url": "https://mycompany.com/community",
            "support_email": "support@mycompany.com",
            "company_name": "MyCompany"
        })
        
        print("Welcome Email Template:")
        print("-" * 30)
        print(result)
        print("-" * 30)
        
    except Exception as e:
        print(f"Template rendering failed: {e}")
    
    print()


def main():
    """Main demonstration function"""
    print("🚀 Notification Service Demonstration")
    print("=" * 80)
    print()
    
    # Run demonstrations
    demo_email_channel()
    demo_slack_channel() 
    demo_template_engine()
    demo_deduplication()
    demo_file_templates()
    
    print("✅ All demonstrations completed!")
    print()
    print("📁 Check the 'email_outputs' folder for generated email files.")
    print("📋 See the console output above for Slack messages.")
    print("🔧 Modify the templates in the 'templates' folder to customize messages.")
    print("📖 Check 'examples/usage_examples.py' for more comprehensive examples.")
    print("🧪 Run 'python -m unittest tests.test_notification_service' for tests.")


if __name__ == "__main__":
    main()
