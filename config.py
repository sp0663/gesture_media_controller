# Gesture to VLC command mapping
GESTURE_COMMANDS = {
    'fist': 'mute',
    'open_palm': 'play_pause',
    'pinch': 'full_screen',
    'swipe_right': 'move_next',
    'swipe_left': 'move_prev'
}

# VLC keyboard shortcuts
VLC_KEYS = {
    'play_pause': 'space',
    'mute': 'm',
    'full_screen': 'f',
    'move_next': 'n',
    'move_prev': 'p'
}

# Gesture recognition settings
GESTURE_HOLD_TIME = 0.5  # seconds - how long gesture must be held to trigger
COOLDOWN_TIME = 2.0     # seconds - how long after a gesture can you trigger another
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