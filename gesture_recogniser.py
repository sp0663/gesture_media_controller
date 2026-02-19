from utils import count_extended_fingers, is_pinch, cal_distance
from collections import deque
import time
import math
from config import ACCUMULATION_THRESHOLD, SWIPE_COOLDOWN, SWIPE_THRESHOLD, FLAP_COOLDOWN

class GestureRecogniser:
    def __init__(self, buffer_size=10):
        self.swipe_history = deque(maxlen=buffer_size)
        self.last_swipe_time = 0
        self.last_volume_time = 0  
        self.last_fist_move_time = 0    # Tracks the last time the fist moved even slightly
        self.rotation_accumulator = 0.0
        self.vertical_accumulator = 0.0 
        self.prev_fist_y = None         
        self.prev_angle = None
        self.locked_hand_type = None
    
    def recognise_gesture(self, landmarks, hand_label, frame):
        current_time = time.time()
        count = count_extended_fingers(landmarks)
        current_hand_type = hand_label if hand_label else "Right"
        
        # 1. DEFINE HAND STATE
        middle_folded = landmarks[12][2] > landmarks[9][2]
        ring_folded = landmarks[16][2] > landmarks[13][2]
        is_fist_state = (count == 0 or (middle_folded and ring_folded))
        
        # 2. POSITION TRACKING (Using Knuckle - Landmark 9)
        curr_x, curr_y = landmarks[9][1], landmarks[9][2]
        velocity = 0
        if len(self.swipe_history) > 0:
            prev_x, prev_y = self.swipe_history[-1]
            velocity = math.hypot(curr_x - prev_x, curr_y - prev_y)
        self.swipe_history.append((curr_x, curr_y))

        # 3. PROPORTIONAL VOLUME CONTROL (Fist movement)
        if is_fist_state:
            if self.prev_fist_y is not None:
                dy = curr_y - self.prev_fist_y
                
                # SENSITIVITY FIX: If hand moves more than 2 pixels, it's "moving"
                # This updates the timer to block the static "Mute" gesture
                if abs(dy) > 2:
                    self.last_fist_move_time = current_time
                
                self.vertical_accumulator += dy
                
                # Trigger volume change every 20 pixels for better "slow" control
                volume_step = 20 
                vol_cooldown = FLAP_COOLDOWN if 'FLAP_COOLDOWN' in globals() else 0.15

                if (current_time - self.last_volume_time) > vol_cooldown:
                    if self.vertical_accumulator < -volume_step: # Moving UP
                        self.last_volume_time = current_time
                        self.vertical_accumulator = 0 
                        return 'swipe_fist_up'
                    elif self.vertical_accumulator > volume_step: # Moving DOWN
                        self.last_volume_time = current_time
                        self.vertical_accumulator = 0
                        return 'swipe_fist_down'
            
            self.prev_fist_y = curr_y
        else:
            self.prev_fist_y = None
            self.vertical_accumulator = 0

        # 4. HORIZONTAL SWIPES (Next/Prev)
        if count == 5 and (current_time - self.last_swipe_time) > SWIPE_COOLDOWN:
            if len(self.swipe_history) == self.swipe_history.maxlen:
                start_x = self.swipe_history[0][0]
                total_dx = curr_x - start_x
                if abs(total_dx) > SWIPE_THRESHOLD:
                    self.last_swipe_time = current_time
                    self.swipe_history.clear()
                    return 'swipe_right' if total_dx > 0 else 'swipe_left'

        # 5. REFINED STATIC BLOCKER
        # A: Block if moving fast (General)
        if velocity > 20: 
            return 'unknown'
        
        # B: THE VOLUME PROTECTION LOGIC
        # If the fist moved at all in the last 0.5 seconds, block the static "Mute" (fist) return.
        # This prevents accidental mutes while you are moving your hand slowly.
        if is_fist_state and (current_time - self.last_fist_move_time < 0.5):
            return 'unknown'

        # 6. STATIC FIST (Mute)
        # Only triggers if the hand is a fist AND has been perfectly still for 0.5s
        if is_fist_state:
            return 'fist'

        # 7. PINCH LOGIC
        if is_pinch(landmarks):
            pinch_cx = (landmarks[4][1] + landmarks[8][1]) / 2
            pinch_cy = (landmarks[4][2] + landmarks[8][2]) / 2
            dx = pinch_cx - landmarks[0][1]
            dy = pinch_cy - landmarks[0][2]
            current_angle = math.degrees(math.atan2(dy, dx))
            
            delta = 0
            if self.prev_angle is not None:
                delta = current_angle - self.prev_angle
                if delta > 180: delta -= 360
                elif delta < -180: delta += 360
            else:
                self.prev_angle = current_angle
                self.locked_hand_type = current_hand_type
                return 'unknown'

            self.prev_angle = current_angle
            abs_delta = abs(delta)

            if abs_delta > 1.5:
                effective_delta = -delta if self.locked_hand_type == "Left" else delta
                self.rotation_accumulator += effective_delta
                
                if self.rotation_accumulator > ACCUMULATION_THRESHOLD:
                    self.rotation_accumulator -= ACCUMULATION_THRESHOLD
                    return 'pinch_clockwise'
                elif self.rotation_accumulator < -ACCUMULATION_THRESHOLD:
                    self.rotation_accumulator += ACCUMULATION_THRESHOLD
                    return 'pinch_anticlockwise'
                return 'unknown'
            elif abs_delta > 0.5:
                return 'unknown'
            else:
                return 'pinch'
        else:
            self.prev_angle = None
            self.locked_hand_type = None

        # 8. OPEN PALM (Play/Pause)
        wrist_y = landmarks[0][2]
        knuckle_y = landmarks[9][2]
        hand_size = cal_distance(landmarks[0], landmarks[9]) or 1
        vertical_ratio = (wrist_y - knuckle_y) / hand_size
        
        if count == 5 and vertical_ratio > 0.5:
            return 'open_palm'
            
        return 'unknown'