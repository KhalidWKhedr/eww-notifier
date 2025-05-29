"""
Icon configuration module for the notification system.
Contains all icon-related constants and settings.
"""

from eww_notifier.config import HOME, SYSTEM_ICON_DIRS, USR_SHARE, USR_LOCAL

# Icon search paths (in order of priority)
ICON_DIRS = [
    str(HOME / ".local/share/icons"),
    str(HOME / ".icons"),
    str(USR_SHARE / "icons"),
    str(USR_LOCAL / "icons"),
] + [str(path) for path in SYSTEM_ICON_DIRS]

# Icon extensions and sizes
ICON_EXTENSIONS = [".svg", ".png", ".xpm"]
ICON_SIZES = ["scalable", "512", "256", "128", "96", "64", "48", "32", "24", "16"]

# Default icons for common applications
APP_ICONS = {
    # System icons
    'default': 'dialog-information',
    'system': 'system',
    'update': 'system-software-update',
    'error': 'dialog-error',
    'warning': 'dialog-warning',
    'success': 'dialog-ok',
    'info': 'dialog-information',
    'notify-send': 'dialog-information',
    
    # Browsers
    'firefox': 'firefox',
    'chrome': 'google-chrome',
    'brave': 'brave-browser',
    'chromium': 'chromium',
    'opera': 'opera',
    'vivaldi': 'vivaldi',
    'edge': 'microsoft-edge',
    
    # Communication
    'telegram': 'telegram',
    'discord': 'discord',
    'slack': 'slack',
    'signal': 'signal',
    'whatsapp': 'whatsapp',
    'element': 'element',
    'thunderbird': 'thunderbird',
    'evolution': 'evolution',
    'mail': 'mail',
    
    # Media
    'spotify': 'spotify',
    'vlc': 'vlc',
    'mpv': 'mpv',
    'rhythmbox': 'rhythmbox',
    'clementine': 'clementine',
    'audacious': 'audacious',
    'kodi': 'kodi',
    
    # Development
    'vscode': 'visual-studio-code',
    'code': 'visual-studio-code',
    'sublime': 'sublime-text',
    'atom': 'atom',
    'gedit': 'gedit',
    'kate': 'kate',
    'geany': 'geany',
    
    # System Tools
    'terminal': 'utilities-terminal',
    'file-manager': 'system-file-manager',
    'settings': 'preferences-system',
    'calculator': 'accessories-calculator',
    'calendar': 'calendar',
    'clock': 'clock',
    'weather': 'weather-showers',
    
    # Games
    'steam': 'steam',
    'minecraft': 'minecraft',
    'lutris': 'lutris',
    'wine': 'wine',
    
    # Office
    'libreoffice': 'libreoffice',
    'writer': 'libreoffice-writer',
    'calc': 'libreoffice-calc',
    'impress': 'libreoffice-impress',
    'draw': 'libreoffice-draw',
    
    # Utilities
    'screenshot': 'applets-screenshooter',
    'camera': 'camera',
    'printer': 'printer',
    'scanner': 'scanner',
    'bluetooth': 'bluetooth',
    'wifi': 'network-wireless',
    'battery': 'battery',
    'volume': 'audio-volume-high',
    'brightness': 'display-brightness',
} 