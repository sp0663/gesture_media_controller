from utils import finger_extended, count_extended_fingers, pinch

def recognise_gesture(landmarks):

    count = count_extended_fingers(landmarks)

    if count == 0:
        gesture = 'fist'
    elif count == 5:
        gesture = 'open_palm'
    elif pinch(landmarks):
        gesture = 'pinch'
    else:
        gesture = 'unknown'

    return gesture
