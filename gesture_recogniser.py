from utils import finger_extended, count_extended_fingers, is_pinch

def recognise_gesture(landmarks):

    count = count_extended_fingers(landmarks)
    
    if is_pinch(landmarks):
        gesture = 'pinch'
    elif count == 0:
        gesture = 'fist'
    elif count == 5:
        gesture = 'open_palm'
    else:
        gesture = 'unknown'

    return gesture
