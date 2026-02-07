from utils import count_extended_fingers, is_pinch
from collections import deque
import time

class GestureRecogniser:
    def __init__(self, buffer_size=10):
        self.history = deque(maxlen=buffer_size)
        self.swipe_threshold = 200 # Minimum pixels for a flick
        self.cooldown = 1        # Seconds between swipes
        self.last_swipe_time = 0

    def recognise_gesture(self, landmarks):
        current_time = time.time()
        count = count_extended_fingers(landmarks)
        
        curr_x, curr_y = landmarks[0][1], landmarks[0][2]
        self.history.append((curr_x, curr_y))

        if count == 5 and (current_time - self.last_swipe_time) > self.cooldown:
            if len(self.history) == self.history.maxlen:
                start_x, start_y = self.history[0]
                total_dx = curr_x - start_x
                total_dy = curr_y - start_y

                if abs(total_dx) > self.swipe_threshold and abs(total_dx) > abs(total_dy) * 2:
                    self.last_swipe_time = current_time
                    self.history.clear() # Reset to prevent double triggers
                    return 'swipe_right' if total_dx > 0 else 'swipe_left'

        if is_pinch(landmarks):
            return 'pinch'
        elif count == 0:
            return 'fist'
        elif count == 5:
            return 'open_palm'
            
        return 'unknown'