"""
Utility functions for handling notifications.
"""

import dbus
from typing import Dict, Any, List

from eww_notifier.config import URGENCY_LEVELS


def get_urgency(hints: Dict[str, Any]) -> str:
    """Get the urgency level from hints."""
    if hints and isinstance(hints, dict):
        urgency = hints.get('urgency')
        if urgency is not None:
            return URGENCY_LEVELS.get(urgency, 'normal')
    return 'normal'


def process_actions(actions: List[str]) -> List[Dict[str, str]]:
    """Process notification actions into a list of dictionaries."""
    processed_actions = []
    if actions and isinstance(actions, list):
        for i in range(0, len(actions), 2):
            if i + 1 < len(actions):
                processed_actions.append({
                    'notification_id': actions[i],
                    'label': actions[i + 1]
                })
    return processed_actions


def process_hints(hints: Dict[str, Any]) -> Dict[str, Any]:
    """Process notification hints into a clean dictionary."""
    processed_hints = {}
    if hints and isinstance(hints, dict):
        for key, value in hints.items():
            # Skip byte arrays and D-Bus variants
            if isinstance(value, (dbus.Array, dbus.Byte, dbus.ByteArray)):
                continue
            if isinstance(value, (str, int, float, bool)):
                processed_hints[key] = value
            elif hasattr(value, 'unpack'):
                unpacked = value.unpack()
                # Skip byte arrays in unpacked values too
                if not isinstance(unpacked, (dbus.Array, dbus.Byte, dbus.ByteArray)):
                    processed_hints[key] = unpacked
    return processed_hints 