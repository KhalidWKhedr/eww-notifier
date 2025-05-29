"""
MIT License

Copyright (c) 2024 KhalidWKhedr

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import pytest
from eww_notifier.notifier.notification_processor import NotificationProcessor

def test_notification_processor_initialization():
    """Test that NotificationProcessor initializes correctly."""
    processor = NotificationProcessor()
    assert processor is not None

def test_process_notification():
    """Test basic notification processing."""
    processor = NotificationProcessor()
    notification = {
        "app_name": "test_app",
        "replaces_id": 0,
        "app_icon": "test_icon",
        "summary": "Test Summary",
        "body": "Test Body",
        "actions": [],
        "hints": {},
        "expire_timeout": 5000
    }
    
    result = processor.process_notification(notification)
    assert result is not None
    assert "app_name" in result
    assert "summary" in result
    assert "body" in result

def test_process_spotify_notification():
    """Test Spotify notification processing."""
    processor = NotificationProcessor()
    notification = {
        "app_name": "Spotify",
        "replaces_id": 0,
        "app_icon": "spotify",
        "summary": "Now Playing",
        "body": "Test Song - Test Artist",
        "actions": [],
        "hints": {},
        "expire_timeout": 5000
    }
    
    result = processor.process_notification(notification)
    assert result is not None
    assert result["app_name"] == "Spotify"
    assert "album_art" in result

def test_process_notification_with_actions():
    """Test notification processing with actions."""
    processor = NotificationProcessor()
    notification = {
        "app_name": "test_app",
        "replaces_id": 0,
        "app_icon": "test_icon",
        "summary": "Test Summary",
        "body": "Test Body",
        "actions": ["action1", "Action 1", "action2", "Action 2"],
        "hints": {},
        "expire_timeout": 5000
    }
    
    result = processor.process_notification(notification)
    assert result is not None
    assert "actions" in result
    assert len(result["actions"]) == 2

def test_process_notification_with_hints():
    """Test notification processing with hints."""
    processor = NotificationProcessor()
    notification = {
        "app_name": "test_app",
        "replaces_id": 0,
        "app_icon": "test_icon",
        "summary": "Test Summary",
        "body": "Test Body",
        "actions": [],
        "hints": {
            "urgency": 1,
            "category": "test.category"
        },
        "expire_timeout": 5000
    }
    
    result = processor.process_notification(notification)
    assert result is not None
    assert "urgency" in result
    assert "category" in result 