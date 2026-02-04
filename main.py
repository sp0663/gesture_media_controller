import cv2
import time
from hand_tracker import HandTracker
from gesture_recogniser import recognise_gesture
from media_controller import MediaController
from config import GESTURE_HOLD_TIME, DEBUG,MAX_HANDS

# Setup
tracker = HandTracker(max_hands=MAX_HANDS)
controller = MediaController()
cap = cv2.VideoCapture(0)

# Debouncing variables
gesture_start_time = None
last_gesture = None
triggered = False
last_execution_time=0

print("Gesture Media Controller Started!")
print("Show gestures to control VLC")
print("Press 'q' to quit")

while True:
    success, frame = cap.read()
    current_time = time.time()

    if not success:
        print("Failed to capture frame")
        break
    
    # Detect hand
    frame = tracker.find_hands(frame, draw=True)
    landmarks = tracker.get_landmarks(frame,target_hand='Right')

    # Recognize gesture (only if hand detected)
    if len(landmarks) > 0:
        current_gesture = recognise_gesture(landmarks)
        
        # Debouncing logic
        if current_gesture == last_gesture:
            if gesture_start_time and (current_time - gesture_start_time) > GESTURE_HOLD_TIME:
                # if current_gesture=='':
                #     if(current_time - last_execution_time)>0.25:
                #         controller.execute_command(current_gesture)
                #         last_execution_time=current_time
                #         if DEBUG: print(f"VolumeAdjusting : {current_gesture}")
                if not triggered and current_gesture != 'unknown':
                    controller.execute_command(current_gesture)
                    triggered = True
                    if DEBUG:
                        print(f"Executed: {current_gesture}")
        else:
            last_gesture = current_gesture 
            gesture_start_time = current_time
            triggered = False
        
        # Display current gesture
        color = (0, 255, 0) if current_gesture != 'unknown' else (0, 165, 255)
        cv2.putText(frame, f"Gesture: {current_gesture}", 
                    (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
        
        # Show hold progress
        if gesture_start_time and current_gesture != 'unknown':
            hold_time = current_time - gesture_start_time
            progress = min(hold_time / GESTURE_HOLD_TIME, 1.0)
            
            bar_width = 200
            bar_height = 20
            filled = int(bar_width * progress)
            
            cv2.rectangle(frame, (10, 90), (10 + bar_width, 90 + bar_height), 
                         (50, 50, 50), -1)
            cv2.rectangle(frame, (10, 90), (10 + filled, 90 + bar_height), 
                         (0, 255, 0), -1)
            cv2.putText(frame, "Hold...", (10, 85), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    else:
        # No hand detected - RESET ALL
        last_gesture = None
        gesture_start_time = None
        triggered = False
        
        cv2.putText(frame, "No hand detected", 
                    (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Instructions
    cv2.putText(frame, "Fist=mute | Open Palm=pause/play | Q=Quit | Peace_sign=fullscreen", 
                (10, frame.shape[0] - 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

    cv2.imshow("Gesture Media Controller", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
print("Controller stopped!")