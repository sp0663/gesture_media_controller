# Gesture to VLC command mapping
GESTURE_COMMANDS = {
    'fist': 'mute',
    'peace_sign':'pause/play',
    'palm_upward':'volume_up',
    'palm_downward':'volume_down'
}

# VLC keyboard shortcuts
VLC_KEYS = {
    'mute': 'm','pause/play':'space',
    'volume_up':'ctrl+up','volume_down':'ctrl+down'
}

# Gesture recognition settings
GESTURE_HOLD_TIME = 0.2 # seconds - how long gesture must be held to trigger
COOLDOWN_TIME = 2.5   # seconds - how long after a gesture can you trigger another
CONFIDENCE_THRESHOLD = 0.8  

# Hand tracking settings
MAX_HANDS = 2
DETECTION_CONFIDENCE = 0.7
TRACKING_CONFIDENCE = 0.6

# Performance settings
TARGET_FPS = 15
MAX_LATENCY_MS = 200

# Debug mode
DEBUG = True  