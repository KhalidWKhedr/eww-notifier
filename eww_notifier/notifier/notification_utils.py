"""
Utility functions for handling notifications.

This module provides utility functions for:
- Processing notification urgency levels
- Processing notification actions
- Processing notification hints
"""

import logging
import dbus
from typing import Dict, Any, List, Union

from eww_notifier.config import URGENCY_LEVELS
from eww_notifier.utils.error_handler import handle_error, NotificationError

logger = logging.getLogger(__name__)


def get_urgency(hints: Dict[str, Any]) -> str:
    """Get the urgency level from notification hints.
    
    This function:
    1. Extracts urgency from hints
    2. Maps numeric urgency to string level
    3. Falls back to 'normal' if invalid
    
    Args:
        hints: Dictionary of notification hints
        
    Returns:
        Urgency level as string ('low', 'normal', or 'high')
        
    Raises:
        NotificationError: If processing fails
    """
    try:
        if hints and isinstance(hints, dict):
            urgency = hints.get('urgency')
            if urgency is not None:
                level = URGENCY_LEVELS.get(urgency, 'normal')
                logger.debug(f"Got urgency level: {level}")
                return level
        return 'normal'
    except Exception as e:
        handle_error(e, "urgency processing", exit_on_error=False)
        return 'normal'


def process_actions(actions: List[str]) -> List[Dict[str, str]]:
    """Process notification actions into a list of dictionaries.
    
    This function:
    1. Takes a flat list of action pairs
    2. Converts each pair into a dictionary
    3. Handles malformed input gracefully
    
    Args:
        actions: List of action strings in pairs (id, label)
        
    Returns:
        List of action dictionaries with 'notification_id' and 'label'
        
    Raises:
        NotificationError: If processing fails
    """
    try:
        processed_actions = []
        if actions and isinstance(actions, list):
            for i in range(0, len(actions), 2):
                if i + 1 < len(actions):
                    action = {
                        'notification_id': actions[i],
                        'label': actions[i + 1]
                    }
                    processed_actions.append(action)
                    logger.debug(f"Processed action: {action}")
        return processed_actions
    except Exception as e:
        handle_error(e, "action processing", exit_on_error=False)
        return []


def process_hints(hints: Dict[str, Any]) -> Dict[str, Any]:
    """Process notification hints into a clean dictionary.
    
    This function:
    1. Filters out D-Bus specific types
    2. Unpacks D-Bus variants
    3. Keeps only simple types (str, int, float, bool)
    
    Args:
        hints: Dictionary of notification hints
        
    Returns:
        Cleaned dictionary with only simple types
        
    Raises:
        NotificationError: If processing fails
    """
    try:
        processed_hints = {}
        if hints and isinstance(hints, dict):
            for key, value in hints.items():
                # Skip byte arrays and D-Bus variants
                if isinstance(value, (dbus.Array, dbus.Byte, dbus.ByteArray)):
                    logger.debug(f"Skipping D-Bus array/byte for key: {key}")
                    continue
                    
                # Handle simple types
                if isinstance(value, (str, int, float, bool)):
                    processed_hints[key] = value
                    logger.debug(f"Processed hint {key}: {value}")
                    
                # Handle D-Bus variants
                elif hasattr(value, 'unpack'):
                    try:
                        unpacked = value.unpack()
                        # Skip byte arrays in unpacked values too
                        if not isinstance(unpacked, (dbus.Array, dbus.Byte, dbus.ByteArray)):
                            processed_hints[key] = unpacked
                            logger.debug(f"Unpacked hint {key}: {unpacked}")
                    except Exception as e:
                        logger.warning(f"Failed to unpack D-Bus variant for key {key}: {e}")
                        
        return processed_hints
    except Exception as e:
        handle_error(e, "hint processing", exit_on_error=False)
        return {} 