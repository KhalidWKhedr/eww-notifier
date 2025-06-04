import os
import tempfile
import time

import pytest

from eww_notifier.notification_queue.notification_queue import NotificationQueue


@pytest.fixture
def temp_notification_file(monkeypatch):
    with tempfile.NamedTemporaryFile(delete=False) as f:
        temp_path = f.name
    monkeypatch.setattr('eww_notifier.config.NOTIFICATION_FILE', temp_path)
    monkeypatch.setattr('eww_notifier.config.NOTIFICATION_TEMP_FILE', temp_path + '.tmp')
    yield temp_path
    os.remove(temp_path)
    if os.path.exists(temp_path + '.tmp'):
        os.remove(temp_path + '.tmp')

def test_queue_initialization(temp_notification_file):
    queue = NotificationQueue()
    assert isinstance(queue.notifications, list)

def test_add_and_get_notification(temp_notification_file):
    queue = NotificationQueue()
    notif = {'notification_id': '1', 'summary': 'Test', 'body': 'Body', 'expire_timeout': 10000, 'timestamp': time.time()}
    queue.add_notification(notif)
    assert any(n['notification_id'] == '1' for n in queue.notifications)

def test_remove_notification(temp_notification_file):
    queue = NotificationQueue()
    notif = {'notification_id': '2', 'summary': 'Test2', 'body': 'Body2', 'expire_timeout': 10000, 'timestamp': time.time()}
    queue.add_notification(notif)
    queue.remove_notification('2')
    assert not any(n['notification_id'] == '2' for n in queue.notifications)

def test_clear_notifications(temp_notification_file):
    queue = NotificationQueue()
    notif = {'notification_id': '3', 'summary': 'Test3', 'body': 'Body3', 'expire_timeout': 10000, 'timestamp': time.time()}
    queue.add_notification(notif)
    queue.clear()
    assert len(queue.notifications) == 0

def test_expired_notification_cleanup(temp_notification_file):
    queue = NotificationQueue()
    old_notif = {'notification_id': '4', 'summary': 'Old', 'body': 'Old', 'expire_timeout': 1, 'timestamp': time.time() - 10}
    queue.add_notification(old_notif)
    queue._cleanup_old_notifications()
    assert not any(n['notification_id'] == '4' for n in queue.notifications) 