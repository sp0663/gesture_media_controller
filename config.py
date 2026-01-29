# Gesture to VLC command mapping
GESTURE_COMMANDS = {
    'fist': 'mute',
    'open_palm': 'play_pause',
    'peace_sign':'volume_up'
}

# VLC keyboard shortcuts
VLC_KEYS = {
    'play_pause': 'space',
    'mute': 'm','volume_up':'ctrl+up'
}

# Gesture recognition settings
GESTURE_HOLD_TIME = 0.6 # seconds - how long gesture must be held to trigger
COOLDOWN_TIME = 1.5    # seconds - how long after a gesture can you trigger another
CONFIDENCE_THRESHOLD = 0.8  

# Hand tracking settings
MAX_HANDS = 1
DETECTION_CONFIDENCE = 0.65
TRACKING_CONFIDENCE = 0.5

# Performance settings
TARGET_FPS = 15
MAX_LATENCY_MS = 200

# Debug mode
DEBUG = True  