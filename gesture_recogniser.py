from utils import count_extended_fingers, is_pinch

class GestureRecogniser:
    def __init__(self):
        self.swipe_start = None

    def recognise_gesture(self, landmarks):
        SWIPE_THRESHOLD = 100  
        count = count_extended_fingers(landmarks)
        
        if is_pinch(landmarks):
            gesture = 'pinch'
            self.swipe_start = None
            
        elif count == 0:
            gesture = 'fist'
            self.swipe_start = None
            
        elif count == 5:
            if self.swipe_start is None:
                self.swipe_start = landmarks[0][1]
                gesture = 'open_palm'
            else:
                movement = landmarks[0][1] - self.swipe_start
                if movement > SWIPE_THRESHOLD:
                    gesture = 'swipe_right'
                elif movement < -SWIPE_THRESHOLD:  
                    gesture = 'swipe_left'
                else:
                    gesture = 'open_palm'
        else:
            gesture = 'unknown'
            self.swipe_start = None
            
        return gesture