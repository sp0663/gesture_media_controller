# Gesture to VLC command mapping
GESTURE_COMMANDS = {
    # --- Standard Geometric Gestures ---
    'fist': 'mute',
    'open_palm': 'play_pause',
    'pinch': 'full_screen',
    'swipe_right': 'move_next',
    'swipe_left': 'move_prev',
    'flap_up': 'volume_up',
    'flap_down': 'volume_down',
    'pinch_clockwise': 'jump_forward',
    'pinch_anticlockwise': 'jump_backward',

    # --- Custom ML Gestures ---
    # Map your trained ML gesture names to any command from the VLC_KEYS list below!
    # Example:
    # 'peace_sign': 'speed_up',
    # 'thumbs_down': 'slow_down',
    # 'spiderman': 'take_snapshot',
}

# Comprehensive VLC keyboard shortcuts
VLC_KEYS = {
    # Core Playback
    'play_pause': 'space',
    'stop': 's',
    'full_screen': 'f',
    
    # Volume Controls
    'mute': 'm',
    'volume_up': 'ctrl+up',
    'volume_down': 'ctrl+down',
    
    # Track & Playlist Navigation
    'move_next': 'n',
    'move_prev': 'p',
    'toggle_loop': 'l',
    'toggle_random': 'r',
    
    # Time Seeking
    'jump_forward': 'alt+right',        # Short jump (+10 seconds)
    'jump_backward': 'alt+left',        # Short jump (-10 seconds)
    'jump_forward_long': 'ctrl+right',  # Medium jump (+1 minute)
    'jump_backward_long': 'ctrl+left',  # Medium jump (-1 minute)
    
    # Playback Speed
    'speed_up': ']',
    'slow_down': '[',
    'normal_speed': '=',
    
    # Media & Tracks
    'next_subtitle': 'v',
    'next_audio_track': 'b',
    
    # App & Utility Controls
    'take_snapshot': 'shift+s',
    'show_time': 't',
    'quit_vlc': 'ctrl+q'
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

GESTURE_COMMANDS['peace'] = 'take_snapshot'
