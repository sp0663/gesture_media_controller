from utils import finger_extended, count_extended_fingers,peace_sign,volume

def recognise_gesture(landmarks):
    gesture='unknown'

    count = count_extended_fingers(landmarks)
    if count == 0:
        gesture = 'fist'
    elif count==2:
        gesture=peace_sign(landmarks)
    elif count>=4:
        result=gesture=volume(landmarks)
        if result:
            gesture=result
    

    return gesture
 