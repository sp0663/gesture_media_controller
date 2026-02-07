import cv2
import numpy as np
import time
from hand_tracker import HandTracker
from gesture_recogniser import recognise_gesture
from media_controller import MediaController 
from config import GESTURE_HOLD_TIME, DEBUG, MAX_HANDS,COOLDOWN_TIME

# Setup
# 1. Initialize Tracker with config setting for 2 hands
tracker = HandTracker(max_hands=MAX_HANDS)
controller = MediaController()
cap = cv2.VideoCapture(0)

# Variables for logic
gesture_start_time = None
last_gesture = None
gesture_start_y = None 
prev_y=None   # Tracks where the hand started for volume control
triggered = False        # Prevents static gestures from firing multiple times
last_execution_time = 0  # Limits speed of volume changes
SLIDE_SENSITIVITY=0.03
print("Gesture Media Controller Started!")
print("Show gestures to control VLC")
print("Press 'q' to quit")

# ... (Imports and Setup remain the same) ...

# Cleaned up variables (Removed gesture_start_y as we don't need it anymore!)
gesture_start_time = None
last_gesture = None
triggered = False
last_execution_time = 0

while True:
    success, frame = cap.read()
    current_time = time.time()

    if not success:
        break
    
    # 1. Detect Hand
    frame = tracker.find_hands(frame, draw=True)
    landmarks = tracker.get_landmarks(frame, target_hand='Right')

    # 2. Recognize Gesture
    if len(landmarks) > 0:
        current_gesture = recognise_gesture(landmarks)
        
        # --- FIX: Sticky Logic (Keeps 'open_palm' stable even if you rotate hand) ---
        if current_gesture == 'unknown' and last_gesture == 'open_palm':
            current_gesture = 'open_palm'
        
        # 3. Main Logic
        if current_gesture == last_gesture and gesture_start_time is not None:
            duration = current_time - gesture_start_time
            
            # =================================================================
            #  "SWIPE-UP" CONTROL (Pitch-Based Volume)
            # =================================================================
            if current_gesture == 'open_palm':
                #reset static gestures
                last_gesture=None
                triggered=False
                gesture_start_time=None
                h,w,c=frame.shape
                current_y=[landmarks[8][2]/h,landmarks[12][2]/h,landmarks[16][2]/h,landmarks[20][2]]
                if gesture_start_y is None:
                    gesture_start_y=current_y
                    prev_y=current_y
                    cv2.putText(frame,"Volume Locked",(10,100),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,255),2)
                else:
                    movement=np.array(prev_y)-np.array(current_y)
                    if np.all(movement>SLIDE_SENSITIVITY):
                        controller.execute_command('palm_upward')
                        prev_y=current_y
                        cv2.putText(frame,"VOL_UP^",(10,100),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
                    elif np.all(movement<-SLIDE_SENSITIVITY):
                        controller.execute_command('palm_downward')
                        prev_y=current_y
                        cv2.putText(frame,"VOL_DOWN^",(10,100),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)


            # =================================================================
            # STATIC GESTURES (Mute / Fullscreen)
            # =================================================================
            elif duration > GESTURE_HOLD_TIME:
                # Cooldown check to prevent accidental Mute after Volume change
                if (current_time - last_execution_time) > COOLDOWN_TIME:
                    if not triggered and current_gesture != 'unknown':
                        controller.execute_command(current_gesture)
                        triggered = True
                        last_execution_time = current_time
                        if DEBUG: print(f"Executed Static: {current_gesture}")

        else:
            # Gesture Changed
            last_gesture = current_gesture 
            gesture_start_time = current_time
            triggered = False
        
        # Display Info
        color = (0, 255, 0) if current_gesture != 'unknown' else (0, 165, 255)
        cv2.putText(frame, f"Gesture: {current_gesture}", (10, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

        # Progress Bar (Only for static gestures, not volume)
        if gesture_start_time and current_gesture != 'open_palm':
            hold_time = current_time - gesture_start_time
            progress = min(hold_time / GESTURE_HOLD_TIME, 1.0)
            bar_width = 200
            filled = int(bar_width * progress)
            cv2.rectangle(frame, (10, 90), (10 + bar_width, 110), (50, 50, 50), -1)
            cv2.rectangle(frame, (10, 90), (10 + filled, 110), (0, 255, 0), -1)
            cv2.putText(frame, "Hold...", (10, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    else:
        last_gesture = None
        gesture_start_time = None
        triggered = False
        cv2.putText(frame, "No hand detected", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Gesture Media Controller", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
