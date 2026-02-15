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
    if not success: break
    
    frame = tracker.find_hands(frame)
    landmarks, hand_label = tracker.get_landmarks(frame)

    if landmarks:
        current_gesture = recon.recognise_gesture(landmarks, hand_label, frame)
        
        # Immediate Trigger for Swipes (The recogniser handles the timing)
        if 'swipe' in current_gesture:
            controller.execute_command(current_gesture)
            triggered = True
            last_gesture = current_gesture
            if DEBUG: print(f"Swipe Detected: {current_gesture}")

        elif 'flap' in current_gesture:
            controller.execute_command(current_gesture)
            triggered = True
            last_gesture = current_gesture
            if DEBUG: print(f"Flap Detected: {current_gesture}")

        elif 'pinch_' in current_gesture:
            controller.execute_command(current_gesture)
            triggered = True
            last_gesture = current_gesture
            if DEBUG: print(f"Pinch movement Detected: {current_gesture}")

        # Debounce Logic for Static Gestures (Fist, Pinch, Palm)
        elif current_gesture == last_gesture and current_gesture != 'unknown':
            hold_duration = time.time() - gesture_start_time
            if hold_duration > GESTURE_HOLD_TIME and not triggered:
                controller.execute_command(current_gesture)
                triggered = True
                if DEBUG: print(f"Held Gesture Executed: {current_gesture}")
        
        # Reset if gesture changes
        elif current_gesture != last_gesture:
            last_gesture = current_gesture
            gesture_start_time = time.time()
            triggered = False
        # Display current gesture
        color = (0, 255, 0) if current_gesture != 'unknown' else (0, 165, 255)
        cv2.putText(frame, f"Gesture: {current_gesture}", 
                    (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
        
        # Show hold progress
        if gesture_start_time and current_gesture != 'unknown':
            hold_time = time.time() - gesture_start_time
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
        last_gesture = None
        triggered = False

    cv2.imshow("Gesture Media Controller", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break