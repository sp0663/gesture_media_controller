# Gesture to VLC command mapping
GESTURE_COMMANDS = {
    'fist': 'mute',
    'open_palm': 'play_pause',
    'pinch': 'full_screen',
    'swipe_right': 'move_next',
    'swipe_left': 'move_prev',
    'flap_up': 'volume_up',
    'flap_down': 'volume_down',
    'pinch_clockwise': 'jump_forward',
    'pinch_anticlockwise': 'jump_backward'
}

# VLC keyboard shortcuts
VLC_KEYS = {
    'play_pause': 'space',
    'mute': 'm',
    'full_screen': 'f',
    'move_next': 'n',
    'move_prev': 'p',
    'volume_up': 'ctrl+up',
    'volume_down': 'ctrl+down',
    'jump_forward': 'alt+right',
    'jump_backward': 'alt+left'
}

# Gesture recognition settings
GESTURE_HOLD_TIME = 0.5  # seconds - how long gesture must be held to trigger
ACCUMULATION_THRESHOLD = 10.0
SWIPE_COOLDOWN = 1
FLAP_COOLDOWN = 0.15
SWIPE_THRESHOLD = 200
FLAP_THRESHOLD = 30

# Hand tracking settings
MAX_HANDS = 1
DETECTION_CONFIDENCE = 0.5
TRACKING_CONFIDENCE = 0.5

# Performance settings
TARGET_FPS = 15
MAX_LATENCY_MS = 200

# Debug mode
DEBUG = True  