from utils import finger_extended, count_extended_fingers,peace_sign

def recognise_gesture(landmarks):

    count = count_extended_fingers(landmarks)

    if count == 0:
        gesture = 'fist'
    elif count == 5:
        gesture = 'open_palm'
    elif count==2:
        gesture=peace_sign(landmarks)
    else:
        gesture = 'unknown'

    return gesture
 