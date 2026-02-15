from utils import count_extended_fingers, is_pinch, cal_angle, cntr_pt
from collections import deque
import time
from config import ACCUMULATION_THRESHOLD, SWIPE_COOLDOWN, FLAP_COOLDOWN, SWIPE_THRESHOLD, FLAP_THRESHOLD

class GestureRecogniser:
    def __init__(self, buffer_size=10):
        self.swipe_history = deque(maxlen=buffer_size)    # Swipe - Palm position history
        self.last_swipe_time = 0    # Swipe - Last swipe seen
        self.rotation_accumulator = 0.0     # Pinch rotate - Rotation angle history
        self.prev_angle = None      # Pinch rotate - Last pinch rotation angle  
        self.locked_hand_type = None    # Pinch rotate - Locked hand label
        self.last_flap_time = 0     # Flap - Last flap seen
    

    def recognise_gesture(self, landmarks, hand_label, frame):
        current_time = time.time()
        count = count_extended_fingers(landmarks)
        
        # Swipe Variables
        curr_x, curr_y = landmarks[0][1], landmarks[0][2]
        self.swipe_history.append((curr_x, curr_y))

        # Pinch Rotate Variables
        is_locked = False
        center_point = cntr_pt(landmarks)
        active_hand_type = self.locked_hand_type if self.locked_hand_type else "None"


        # Dynamic Gesture Detection

        # Swipe        
        if count == 5 and (current_time - self.last_swipe_time) > SWIPE_COOLDOWN:
            if len(self.swipe_history) == self.swipe_history.maxlen:
                start_x, start_y = self.swipe_history[0]
                total_dx = curr_x - start_x
                total_dy = curr_y - start_y

                if abs(total_dx) > SWIPE_THRESHOLD and abs(total_dx) > abs(total_dy) * 2:
                    self.last_swipe_time = current_time
                    self.swipe_history.clear() # Reset to prevent double triggers
                    return 'swipe_right' if total_dx > 0 else 'swipe_left'

        # Flap
        if count == 5 and (current_time - self.last_flap_time) > FLAP_COOLDOWN:
            tip_y = landmarks[12][2]
            orientation = curr_y - tip_y

            # CASE 1: Fingers Pointing UP -> Volume UP
            if orientation > FLAP_THRESHOLD:
                self.last_flap_time = current_time
                return 'flap_up'

            # CASE 2: Fingers Pointing DOWN -> Volume DOWN
            elif orientation < -FLAP_THRESHOLD:
                self.last_flap_time = current_time
                return 'flap_down'

        # Pinch Rotate
        if is_pinch(landmarks):
            is_locked = True
            current_angle = cal_angle(landmarks[4], [0,0,0], landmarks[8])
            current_hand_type = hand_label

            if self.prev_angle is None:
                # Lock the hand type on first pinch
                self.locked_hand_type = current_hand_type
                active_hand_type = current_hand_type
                self.prev_angle = current_angle
                self.rotation_accumulator = 0
            
            else:
                delta = current_angle - self.prev_angle
                if delta > 180: delta -= 360
                elif delta < -180: delta += 360
                if self.locked_hand_type == "Left":
                    effective_delta = -delta 
                else:
                    effective_delta = delta  

                self.rotation_accumulator += effective_delta
                
                if self.rotation_accumulator > ACCUMULATION_THRESHOLD:
                    self.rotation_accumulator -= ACCUMULATION_THRESHOLD
                    self.prev_angle = current_angle
                    return 'pinch_clockwise'
                    
                elif self.rotation_accumulator < -ACCUMULATION_THRESHOLD:
                    self.rotation_accumulator += ACCUMULATION_THRESHOLD
                    self.prev_angle = current_angle 
                    return 'pinch_anticlockwise'

                
        # Static gestures detection

        if is_pinch(landmarks):
            return 'pinch'
        elif count == 0:
            return 'fist'
        elif count == 5:
            return 'open_palm'
            
        return 'unknown'