"""
Tests for the notification service

This file contains comprehensive tests for all components of the notification service.
"""

import unittest
import os
import tempfile
from datetime import datetime
from unittest.mock import patch, MagicMock

from src.core.container import Container
from src.core.models import NotificationConfig, NotificationEvent, NotificationMessage
from src.channels.email import EmailChannel
from src.channels.slack import SlackChannel
from src.templates.jinja2_engine import Jinja2TemplateEngine
from src.events.realtime import RealtimeEventSource
from src.events.scheduled import ScheduledEventSource
from src.deduplication.content_based import ContentBasedDeduplicationPolicy
from src.registry.notification_registry import NotificationRegistry


class TestNotificationService(unittest.TestCase):
    """Test suite for the notification service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.container = Container()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures"""
        # Clean up temporary files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_email_channel_send(self):
        """Test email channel sending"""
        email_channel = EmailChannel(output_dir=self.temp_dir)
        
        result = email_channel.send(
            message="Test message",
            recipient="test@example.com",
            subject="Test Subject"
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.channel, "email")
        self.assertEqual(result.recipient, "test@example.com")
        
        # Check if file was created
        files = os.listdir(self.temp_dir)
        self.assertEqual(len(files), 1)
        
        # Check file content
        with open(os.path.join(self.temp_dir, files[0]), 'r') as f:
            content = f.read()
            self.assertIn("Test Subject", content)
            self.assertIn("Test message", content)
            self.assertIn("test@example.com", content)
    
    def test_email_channel_invalid_recipient(self):
        """Test email channel with invalid recipient"""
        email_channel = EmailChannel(output_dir=self.temp_dir)
        
        result = email_channel.send(
            message="Test message",
            recipient="invalid-email"
        )
        
        self.assertFalse(result.success)
        self.assertIn("Invalid email recipient", result.message)
    
    def test_slack_channel_send(self):
        """Test Slack channel sending"""
        slack_channel = SlackChannel()
        
        with patch('builtins.print') as mock_print:
            result = slack_channel.send(
                message="Test message",
                recipient="#test-channel",
                username="Test Bot"
            )
        
        self.assertTrue(result.success)
        self.assertEqual(result.channel, "slack")
        self.assertEqual(result.recipient, "#test-channel")
        mock_print.assert_called_once()
    
    def test_slack_channel_invalid_recipient(self):
        """Test Slack channel with invalid recipient"""
        slack_channel = SlackChannel()
        
        result = slack_channel.send(
            message="Test message",
            recipient="invalid-channel"
        )
        
        self.assertFalse(result.success)
        self.assertIn("Invalid Slack recipient", result.message)
    
    def test_jinja2_template_engine(self):
        """Test Jinja2 template engine"""
        template_dir = os.path.join(self.temp_dir, "templates")
        os.makedirs(template_dir)
        
        # Create a test template
        template_content = "Hello {{ name }}! Welcome to {{ company }}."
        with open(os.path.join(template_dir, "test.txt"), 'w') as f:
            f.write(template_content)
        
        engine = Jinja2TemplateEngine(template_dir)
        
        result = engine.render("test.txt", {"name": "John", "company": "Test Corp"})
        
        self.assertEqual(result, "Hello John! Welcome to Test Corp.")
    
    def test_jinja2_template_engine_string_render(self):
        """Test Jinja2 template engine string rendering"""
        engine = Jinja2TemplateEngine(self.temp_dir)
        
        result = engine.render_string(
            "Hello {{ name }}!",
            {"name": "Alice"}
        )
        
        self.assertEqual(result, "Hello Alice!")
    
    def test_jinja2_template_variables(self):
        """Test Jinja2 template variable extraction"""
        template_dir = os.path.join(self.temp_dir, "templates")
        os.makedirs(template_dir)
        
        # Create a test template with variables
        template_content = "Hello {{ name }}! Your email is {{ email }}."
        with open(os.path.join(template_dir, "test.txt"), 'w') as f:
            f.write(template_content)
        
        engine = Jinja2TemplateEngine(template_dir)
        variables = engine.get_template_variables("test.txt")
        
        self.assertIn("name", variables)
        self.assertIn("email", variables)
    
    def test_realtime_event_source(self):
        """Test real-time event source"""
        source = RealtimeEventSource()
        
        # Add events
        source.add_event("test_event", {"user": "john", "action": "login"})
        source.add_event("test_event", {"user": "jane", "action": "signup"})
        
        # Get events
        events = source.get_events()
        
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].event_type, "test_event")
        self.assertEqual(events[0].data["user"], "john")
        self.assertEqual(events[1].data["user"], "jane")
    
    def test_realtime_event_source_filter(self):
        """Test real-time event source filtering"""
        source = RealtimeEventSource()
        
        # Add events
        source.add_event("login", {"user": "john"})
        source.add_event("signup", {"user": "jane"})
        
        # Get filtered events
        events = source.get_events(event_type="login")
        
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, "login")
    
    def test_scheduled_event_source(self):
        """Test scheduled event source"""
        source = ScheduledEventSource()
        
        # Register a query
        source.register_query(
            name="test_query",
            query="SELECT * FROM test",
            event_type="test_event"
        )
        
        # Set mock data
        mock_data = [{"id": 1, "name": "test"}]
        source.set_mock_data("test_query", mock_data)
        
        # Get events
        events = source.get_events(query_name="test_query")
        
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, "test_event")
        self.assertEqual(events[0].data["id"], 1)
    
    def test_content_based_deduplication(self):
        """Test content-based deduplication policy"""
        policy = ContentBasedDeduplicationPolicy(time_window_hours=1)
        
        # Create identical messages
        message1 = NotificationMessage(
            content="Test message",
            recipient="test@example.com",
            channel="email",
            template="test.txt",
            timestamp=datetime.now()
        )
        
        message2 = NotificationMessage(
            content="Test message",
            recipient="test@example.com",
            channel="email",
            template="test.txt",
            timestamp=datetime.now()
        )
        
        # First message should be sent
        self.assertTrue(policy.should_send(message1, []))
        
        # Add to cache
        policy.add_sent_message(message1)
        
        # Second identical message should not be sent
        self.assertFalse(policy.should_send(message2, policy.get_all_sent_messages()))
    
    def test_deduplication_key_generation(self):
        """Test deduplication key generation"""
        policy = ContentBasedDeduplicationPolicy()
        
        message1 = NotificationMessage(
            content="Test message",
            recipient="test@example.com",
            channel="email",
            template="test.txt"
        )
        
        message2 = NotificationMessage(
            content="Test message",
            recipient="test@example.com",
            channel="email",
            template="test.txt"
        )
        
        # Same messages should have same key
        key1 = policy.get_deduplication_key(message1)
        key2 = policy.get_deduplication_key(message2)
        
        self.assertEqual(key1, key2)
    
    def test_notification_registry(self):
        """Test notification registry"""
        registry = NotificationRegistry(self.container)
        
        # Register a notification
        config = NotificationConfig(
            event_type="test_event",
            channel="slack",
            template="test.txt",
            recipient_field="user_email"
        )
        
        registry.register_notification(config)
        
        # Get configurations
        configs = registry.get_configurations("test_event")
        
        self.assertEqual(len(configs), 1)
        self.assertEqual(configs[0].event_type, "test_event")
    
    def test_notification_registry_summary(self):
        """Test notification registry summary"""
        registry = NotificationRegistry(self.container)
        
        # Register notifications
        config1 = NotificationConfig(
            event_type="signup",
            channel="email",
            template="welcome.txt",
            recipient_field="email"
        )
        
        config2 = NotificationConfig(
            event_type="signup",
            channel="slack",
            template="welcome.txt",
            recipient_field="channel"
        )
        
        registry.register_notifications([config1, config2])
        
        # Get summary
        summary = registry.get_notification_summary()
        
        self.assertEqual(summary["total_configurations"], 2)
        self.assertIn("signup", summary["configurations_by_event_type"])
        self.assertIn("email", summary["configurations_by_channel"])
        self.assertIn("slack", summary["configurations_by_channel"])
    
    def test_container_dependency_injection(self):
        """Test dependency injection container"""
        container = Container()
        
        # Get services
        email_channel = container.get(EmailChannel)
        slack_channel = container.get(SlackChannel)
        template_engine = container.get(Jinja2TemplateEngine)
        
        self.assertIsInstance(email_channel, EmailChannel)
        self.assertIsInstance(slack_channel, SlackChannel)
        self.assertIsInstance(template_engine, Jinja2TemplateEngine)
    
    def test_notification_event_creation(self):
        """Test notification event creation"""
        event = NotificationEvent(
            event_type="test_event",
            data={"user": "john", "action": "login"},
            event_id="test_001",
            source="test"
        )
        
        self.assertEqual(event.event_type, "test_event")
        self.assertEqual(event.data["user"], "john")
        self.assertEqual(event.event_id, "test_001")
        self.assertEqual(event.source, "test")
        self.assertIsInstance(event.timestamp, datetime)
    
    def test_notification_message_creation(self):
        """Test notification message creation"""
        message = NotificationMessage(
            content="Test message",
            recipient="test@example.com",
            channel="email",
            template="test.txt",
            event_id="test_001"
        )
        
        self.assertEqual(message.content, "Test message")
        self.assertEqual(message.recipient, "test@example.com")
        self.assertEqual(message.channel, "email")
        self.assertEqual(message.template, "test.txt")
        self.assertEqual(message.event_id, "test_001")
    
    def test_end_to_end_notification_flow(self):
        """Test complete end-to-end notification flow"""
        # Set up templates
        template_dir = os.path.join(self.temp_dir, "templates")
        os.makedirs(template_dir)
        
        template_content = "Hello {{ name }}! Your email is {{ email }}."
        with open(os.path.join(template_dir, "test.txt"), 'w') as f:
            f.write(template_content)
        
        # Set up container with custom paths
        container = Container()
        container.register(Jinja2TemplateEngine, Jinja2TemplateEngine(template_dir))
        container.register(EmailChannel, EmailChannel(self.temp_dir))
        
        # Set up registry
        registry = NotificationRegistry(container)
        
        # Register notification
        config = NotificationConfig(
            event_type="test_event",
            channel="email",
            template="test.txt",
            recipient_field="email"
        )
        
        registry.register_notification(config)
        
        # Process event
        results = registry.process_event(
            "test_event",
            {"name": "John", "email": "john@example.com"}
        )
        
        # Verify results
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].success)
        self.assertEqual(results[0].channel, "email")
        self.assertEqual(results[0].recipient, "john@example.com")
        
        # Verify file was created
        files = os.listdir(self.temp_dir)
        self.assertEqual(len(files), 1)
        
        # Verify file content
        with open(os.path.join(self.temp_dir, files[0]), 'r') as f:
            content = f.read()
            self.assertIn("Hello John! Your email is john@example.com.", content)


if __name__ == '__main__':
    unittest.main()
