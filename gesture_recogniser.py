from utils import count_extended_fingers, is_pinch, volume, cal_angle
from collections import deque
import time
import numpy as np
from config import ACCUMULATION_THRESHOLD

class GestureRecogniser:
    def __init__(self, buffer_size=10):
        self.history = deque(maxlen=buffer_size)
        self.swipe_threshold = 200 # Minimum pixels for a flick
        self.cooldown = 1        # Seconds between swipes
        self.last_swipe_time = 0
        self.slide_sensitivity = 0.03
        self.slide_error = 0.30
        self.rotation_accumulator = 0.0
        self.prev_angle = None
        self.locked_hand_type = None
    

    def recognise_gesture(self, landmarks, hand_label, frame):
        current_time = time.time()
        count = count_extended_fingers(landmarks)
        
        # Swipe
        curr_x, curr_y = landmarks[0][1], landmarks[0][2]
        self.history.append((curr_x, curr_y))

        # Pinch Rotate
        is_locked = False            
        thumb_pt = np.array(landmarks[4][1:])
        index_pt = np.array(landmarks[8][1:])
        center_pt = (thumb_pt + index_pt) // 2
        center_point = (int(center_pt[0]), int(center_pt[1]))
        active_hand_type = self.locked_hand_type if self.locked_hand_type else "None"

        if count == 5 and (current_time - self.last_swipe_time) > self.cooldown:
            if len(self.history) == self.history.maxlen:
                start_x, start_y = self.history[0]
                total_dx = curr_x - start_x
                total_dy = curr_y - start_y

                if abs(total_dx) > self.swipe_threshold and abs(total_dx) > abs(total_dy) * 2:
                    self.last_swipe_time = current_time
                    self.history.clear() # Reset to prevent double triggers
                    return 'swipe_right' if total_dx > 0 else 'swipe_left'

        elif volume(landmarks):
            h, w, c = frame.shape
            current_y=[landmarks[8][2]/h,landmarks[12][2]/h,landmarks[16][2]/h,landmarks[20][2]]
            prev_y=current_y
            movement=np.array(prev_y)-np.array(current_y)
            if np.all(movement>self.slide_sensitivity) and (abs(landmarks[0][2]/h- landmarks[16][2]/h)<self.slide_error):
                return 'palm_upward'
                prev_y=current_y
            elif np.all(movement<-self.slide_sensitivity) and (landmarks[0][2]/h- landmarks[16][2]/h<self.slide_error):
                prev_y=current_y
                return 'palm_downward'
        
        elif is_pinch(landmarks):
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

                

        if is_pinch(landmarks):
            return 'pinch'
        elif count == 0:
            return 'fist'
        elif count == 5:
            return 'open_palm'
            
        return 'unknown'