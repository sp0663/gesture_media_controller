# Gesture to VLC command mapping
GESTURE_COMMANDS = {
    'fist': 'play_pause',
    'open_palm': 'stop'
}

# VLC keyboard shortcuts
VLC_KEYS = {
    'play_pause': 'space',
    'stop': 's'
}

# Gesture recognition settings
GESTURE_HOLD_TIME = 0.5  # seconds - how long gesture must be held to trigger
CONFIDENCE_THRESHOLD = 0.8  

# Hand tracking settings
MAX_HANDS = 1
DETECTION_CONFIDENCE = 0.5
TRACKING_CONFIDENCE = 0.5

# Performance settings
TARGET_FPS = 15
MAX_LATENCY_MS = 200

# Debug mode
DEBUG = True  