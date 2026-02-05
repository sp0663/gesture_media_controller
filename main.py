import cv2
import time
from hand_tracker import HandTracker
from gesture_recogniser import GestureRecogniser
from media_controller import MediaController
from config import GESTURE_HOLD_TIME, DEBUG

# Setup
tracker = HandTracker()
controller = MediaController()
recon = GestureRecogniser()
cap = cv2.VideoCapture(0)

# Debouncing variables
gesture_start_time = None
last_gesture = None
triggered = False

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
    landmarks = tracker.get_landmarks(frame)

    # Recognize gesture (only if hand detected)
    if len(landmarks) > 0:
        current_gesture = recon.recognise_gesture(landmarks)
        
        wrist_x = landmarks[0][1]
        print(f"Gesture: {current_gesture} | Wrist X: {wrist_x} | Swipe Start: {recon.swipe_start}")
    
        # Debouncing logic
        if current_gesture == last_gesture:
            if current_gesture in ['swipe_right', 'swipe_left']:
                if not triggered:
                    controller.execute_command(current_gesture)
                    recon.swipe_start = None
                    triggered = True
                    if DEBUG:
                        print(f"Executed: {current_gesture}")
            elif gesture_start_time and (current_time - gesture_start_time) > GESTURE_HOLD_TIME:
                if not triggered and current_gesture != 'unknown':
                    controller.execute_command(current_gesture)
                    recon.swipe_start = None
                    triggered = True
                    if DEBUG:
                        print(f"Executed: {current_gesture}")
        else:
            recon.swipe_start = None
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
    cv2.putText(frame, "Fist=Play/Pause | Open Palm=Stop | Q=Quit", 
                (10, frame.shape[0] - 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

    cv2.imshow("Gesture Media Controller", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
print("Controller stopped!")