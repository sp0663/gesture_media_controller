import cv2
import time
import os
from hand_tracker import HandTracker
from gesture_recogniser import GestureRecogniser
from media_controller import MediaController
from config import GESTURE_HOLD_TIME, DEBUG

# Fix NPU Driver link
os.environ["LD_LIBRARY_PATH"] = "/usr/lib/x86_64-linux-gnu:" + os.environ.get("LD_LIBRARY_PATH", "")

# Setup
tracker = HandTracker()
controller = MediaController()
recon = GestureRecogniser()
cap = cv2.VideoCapture(0)

# Timing and State variables
prev_time = 0
gesture_start_time = None
last_gesture = None
triggered = False
gestures_enabled = True 

def draw_skeleton(frame, landmarks):
    """Manually draw the hand lines since MediaPipe's drawer is gone."""
    connections = [
        (0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8),
        (5, 9), (9, 10), (10, 11), (11, 12), (9, 13), (13, 14), (14, 15), 
        (15, 16), (13, 17), (17, 18), (18, 19), (19, 20), (0, 17)
    ]
    for start, end in connections:
        cv2.line(frame, (landmarks[start][1], landmarks[start][2]), 
                 (landmarks[end][1], landmarks[end][2]), (0, 255, 0), 2)
    for lm in landmarks:
        cv2.circle(frame, (lm[1], lm[2]), 5, (0, 0, 255), -1)

def draw_debug_overlay(frame, recon):
    h, w, _ = frame.shape
    history = list(recon.swipe_history)
    if len(history) > 1:
        for i in range(len(history) - 1):
            pt1 = (int(history[i][0]), int(history[i][1]))
            pt2 = (int(history[i+1][0]), int(history[i+1][1]))
            cv2.line(frame, pt1, pt2, (0, 255, 255), 2) 

    cv2.rectangle(frame, (w - 220, 0), (w, 120), (0, 0, 0), -1)
    cv2.putText(frame, f"Rot Accum: {recon.rotation_accumulator:.1f}", (w - 210, 30), 1, 0.6, (255, 0, 255), 2)
    cv2.putText(frame, f"Swipe Buffer: {len(recon.swipe_history)}", (w - 210, 60), 1, 0.6, (0, 255, 255), 2)
    
    lock_status = recon.locked_hand_type if recon.locked_hand_type else "None"
    color = (0, 255, 0) if recon.locked_hand_type else (0, 0, 255)
    cv2.putText(frame, f"Lock: {lock_status}", (w - 210, 90), 1, 0.6, color, 2)

print("Gesture Media Controller Started!")

while True:
    success, frame = cap.read()
    if not success: break
    
    # --- FPS CALCULATION ---
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time)
    prev_time = curr_time
    
    frame = cv2.flip(frame, 1)  
    frame = tracker.find_hands(frame)
    landmarks, hand_label = tracker.get_landmarks(frame)

    # Display FPS in corner
    cv2.putText(frame, f"FPS: {int(fps)}", (frame.shape[1] - 100, 150), 1, 1, (0, 255, 0), 2)

    if landmarks:
        # Draw the skeleton manually
        draw_skeleton(frame, landmarks)
        
        current_gesture = recon.recognise_gesture(landmarks, hand_label, frame)
        
        # 1. TOGGLE LOGIC
        if current_gesture == 'index_pointing':
            if current_gesture != last_gesture:
                gesture_start_time = time.time()
                triggered = False
                last_gesture = current_gesture 
            
            hold_duration = time.time() - gesture_start_time
            if hold_duration > 2.0 and not triggered:
                gestures_enabled = not gestures_enabled
                triggered = True
                
        # 2. NORMAL GESTURES
        elif gestures_enabled:
            if 'swipe' in current_gesture or 'fist_move_' in current_gesture or 'pinch_' in current_gesture:
                controller.execute_command(current_gesture)
                triggered = True
                last_gesture = current_gesture

            elif current_gesture == last_gesture and current_gesture != 'unknown':
                hold_duration = time.time() - gesture_start_time
                if hold_duration > GESTURE_HOLD_TIME and not triggered:
                    controller.execute_command(current_gesture)
                    triggered = True
            
            elif current_gesture != last_gesture:
                last_gesture = current_gesture
                gesture_start_time = time.time()
                triggered = False
        
        else:
            last_gesture = None
            triggered = False
        
        # 3. UI OVERLAY
        if not gestures_enabled:
            cv2.putText(frame, "SYSTEM DISABLED", (10, 50), 1, 1.2, (0, 0, 255), 3)
            progress_label = "Hold Index to Enable"
        else:
            color = (0, 255, 0) if current_gesture != 'unknown' else (0, 165, 255)
            cv2.putText(frame, f"Gesture: {current_gesture}", (10, 50), 1, 1.2, color, 3)
            progress_label = "Hold..."
        
        if gesture_start_time and current_gesture != 'unknown':
            hold_time = time.time() - gesture_start_time
            target = 2.0 if current_gesture == 'index_pointing' else GESTURE_HOLD_TIME
            progress = min(hold_time / target, 1.0)
            cv2.rectangle(frame, (10, 90), (10 + int(200 * progress), 110), (0, 255, 0), -1)
            cv2.rectangle(frame, (10, 90), (210, 110), (255, 255, 255), 1)
            cv2.putText(frame, progress_label, (10, 85), 1, 0.5, (255, 255, 255), 1)
            
    else:
        last_gesture = None
        triggered = False
    
    if DEBUG: draw_debug_overlay(frame, recon)

    cv2.imshow("Gesture Media Controller", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()