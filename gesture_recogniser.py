from utils import count_extended_fingers, is_pinch, cal_distance
from collections import deque
import time
import math
import pickle
import os
from config import ACCUMULATION_THRESHOLD, SWIPE_COOLDOWN, SWIPE_THRESHOLD

class GestureRecogniser:
    def __init__(self, buffer_size=10):
        self.swipe_history = deque(maxlen=buffer_size)    
        self.last_swipe_time = 0    
        self.rotation_accumulator = 0.0     
        self.prev_angle = None      
        self.locked_hand_type = None    
        
        # Load the custom ML model if it exists
        self.custom_model = None
        if os.path.exists("gesture_model.pkl"):
            try:
                with open("gesture_model.pkl", "rb") as f:
                    self.custom_model = pickle.load(f)
                print("Custom ML Model loaded successfully!")
            except Exception as e:
                print(f"Could not load custom model: {e}")
    
    def recognise_gesture(self, landmarks, hand_label, frame):
        current_time = time.time()
        count = count_extended_fingers(landmarks)
        current_hand_type = hand_label if hand_label else "Right"
        
        # 1. VELOCITY GATE (Blocks Static Gestures during Swipes)
        curr_x, curr_y = landmarks[0][1], landmarks[0][2]
        velocity = 0
        if len(self.swipe_history) > 0:
            prev_x, prev_y = self.swipe_history[-1]
            velocity = math.hypot(curr_x - prev_x, curr_y - prev_y)
        self.swipe_history.append((curr_x, curr_y))
        is_moving = velocity > 20

        # 2. SWIPES (Dynamic - High Priority)
        if count == 5 and (current_time - self.last_swipe_time) > SWIPE_COOLDOWN:
            if len(self.swipe_history) == self.swipe_history.maxlen:
                start_x = self.swipe_history[0][0]
                total_dx = curr_x - start_x
                if abs(total_dx) > SWIPE_THRESHOLD:
                    self.last_swipe_time = current_time
                    self.swipe_history.clear() 
                    return 'swipe_right' if total_dx > 0 else 'swipe_left'

        # 3. RIGID FLAP (Volume - Dynamic)
        wrist_y = landmarks[0][2]
        knuckle_y = landmarks[9][2]
        hand_size = cal_distance(landmarks[0], landmarks[9]) or 1
        vertical_ratio = (wrist_y - knuckle_y) / hand_size
        is_horizontal = abs(vertical_ratio) < 0.3

        if is_horizontal and count >= 4:
            tip_y = landmarks[12][2] 
            if tip_y < (knuckle_y - 20): return 'flap_up'
            elif tip_y > (knuckle_y + 20): return 'flap_down'

        # --- STATIC BLOCKER ---
        if is_moving: return 'unknown'
        # ----------------------

        # 4. FIST (Static - Priority over Pinch)
        middle_folded = landmarks[12][2] > landmarks[9][2] 
        ring_folded = landmarks[16][2] > landmarks[13][2]
        if count == 0 or (middle_folded and ring_folded):
            return 'fist'

        # 5. PINCH LOGIC (The Rotation Gate Fix)
        if is_pinch(landmarks):
            # Calculate Center & Angle
            pinch_cx = (landmarks[4][1] + landmarks[8][1]) / 2
            pinch_cy = (landmarks[4][2] + landmarks[8][2]) / 2
            dx = pinch_cx - landmarks[0][1]
            dy = pinch_cy - landmarks[0][2]
            current_angle = math.degrees(math.atan2(dy, dx))
            
            # Rotation Delta Calculation
            delta = 0
            if self.prev_angle is not None:
                delta = current_angle - self.prev_angle
                if delta > 180: delta -= 360
                elif delta < -180: delta += 360
            else:
                self.prev_angle = current_angle
                self.locked_hand_type = current_hand_type
                return 'unknown' # First frame of pinch -> Wait

            # Update Angle State
            self.prev_angle = current_angle
            
            # --- THE 3 ZONES ---
            abs_delta = abs(delta)

            # ZONE 1: HIGH ROTATION (SEEK)
            if abs_delta > 1.5:
                if self.locked_hand_type == "Left": effective_delta = -delta 
                else: effective_delta = delta  
                
                self.rotation_accumulator += effective_delta
                
                # Trigger Seek
                if self.rotation_accumulator > ACCUMULATION_THRESHOLD:
                    self.rotation_accumulator -= ACCUMULATION_THRESHOLD
                    return 'pinch_clockwise'
                elif self.rotation_accumulator < -ACCUMULATION_THRESHOLD:
                    self.rotation_accumulator += ACCUMULATION_THRESHOLD
                    return 'pinch_anticlockwise'
                
                return 'unknown' # Rotating but threshold not met yet

            # ZONE 2: BUFFER ZONE (DEAD ZONE)
            elif abs_delta > 0.5:
                # User is rotating slowly or has shaky hands.
                return 'unknown'

            # ZONE 3: LOW ROTATION (STATIC FULLSCREEN)
            else:
                # Hand is rock solid stable.
                return 'pinch'
        
        else:
            self.prev_angle = None
            self.locked_hand_type = None

        # 6. OPEN PALM (Play/Pause)
        # Using strict vertical check from before
        is_vertical = vertical_ratio > 0.5
        if count == 5 and is_vertical:
            return 'open_palm'
            
        # ---------------------------------------------------------
        # 7. CUSTOM ML GESTURE HOOK
        # ---------------------------------------------------------
        if self.custom_model:
            # Flatten and normalize landmarks exactly as done in training
            wrist_x = landmarks[0][1]
            wrist_y = landmarks[0][2]

            flat_landmarks = []
            for lm in landmarks:
                relative_x = lm[1] - wrist_x
                relative_y = lm[2] - wrist_y
                flat_landmarks.append(relative_x)
                flat_landmarks.append(relative_y)
                
            try:
                prediction = self.custom_model.predict([flat_landmarks])[0]
                # Trigger only if it explicitly recognizes the custom shape
                if prediction == 'custom_gesture':
                    return 'custom_gesture'
            except Exception as e:
                # Fails silently if the model expects different input dimensions
                pass 
                
        return 'unknown'