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

# --- NEW STATE VARIABLE ---
gestures_enabled = True 

print("Gesture Media Controller Started!")
print("Show gestures to control VLC")
print("Press 'q' to quit")

def draw_debug_overlay(frame, recon):
    """
    Draws internal state of the recogniser on the frame.
    """
    h, w, _ = frame.shape
    
    # 1. DRAW SWIPE TRAIL (Yellow)
    history = list(recon.swipe_history)
    if len(history) > 1:
        for i in range(len(history) - 1):
            pt1 = (int(history[i][0]), int(history[i][1]))
            pt2 = (int(history[i+1][0]), int(history[i+1][1]))
            cv2.line(frame, pt1, pt2, (0, 255, 255), 2) 

    # 2. DRAW STATUS PANEL (Top Right Corner)
    cv2.rectangle(frame, (w - 220, 0), (w, 120), (0, 0, 0), -1)
    
    cv2.putText(frame, f"Rot Accum: {recon.rotation_accumulator:.1f}", (w - 210, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)

    cv2.putText(frame, f"Swipe Buffer: {len(recon.swipe_history)}", (w - 210, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    
    lock_status = recon.locked_hand_type if recon.locked_hand_type else "None"
    color = (0, 255, 0) if recon.locked_hand_type else (0, 0, 255)
    cv2.putText(frame, f"Lock: {lock_status}", (w - 210, 90), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

while True:
    success, frame = cap.read()
    if not success: break
    
    frame = cv2.flip(frame, 1)  

    frame = tracker.find_hands(frame)
    landmarks, hand_label = tracker.get_landmarks(frame)

    if landmarks:
        current_gesture = recon.recognise_gesture(landmarks, hand_label, frame)
        
        # 1. HANDLE SYSTEM TOGGLE (Index Pointing)
        # We do this first so it works even when system is disabled
        if current_gesture == 'index_pointing':
            if current_gesture == last_gesture:
                hold_duration = time.time() - gesture_start_time
                if hold_duration > GESTURE_HOLD_TIME and not triggered:
                    gestures_enabled = not gestures_enabled  # TOGGLE STATE
                    triggered = True
                    if DEBUG: print(f"System Enabled: {gestures_enabled}")
            
            # Update timer for the toggle gesture itself
            elif current_gesture != last_gesture:
                last_gesture = current_gesture
                gesture_start_time = time.time()
                triggered = False

        # 2. GUARDED EXECUTION: Only run if system is active
        elif gestures_enabled:
            # Immediate Trigger for Swipes
            if 'swipe' in current_gesture:
                controller.execute_command(current_gesture)
                triggered = True
                last_gesture = current_gesture
                if DEBUG: print(f"Swipe Detected: {current_gesture}")

            # Immediate Trigger for Pinch Rotate
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
            
            # Reset logic for gesture changes
            elif current_gesture != last_gesture:
                last_gesture = current_gesture
                gesture_start_time = time.time()
                triggered = False
        
        # 3. IF DISABLED: Keep updating tracking state so timer doesn't 'jump'
        else:
            if current_gesture != last_gesture:
                last_gesture = current_gesture
                gesture_start_time = time.time()
                triggered = False

        # --- UI DISPLAY ---
        if not gestures_enabled:
            # Show red text when disabled
            cv2.putText(frame, "SYSTEM DISABLED", (10, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
            progress_label = "Hold Index to Enable"
        else:
            # Normal green display when active
            color = (0, 255, 0) if current_gesture != 'unknown' else (0, 165, 255)
            cv2.putText(frame, f"Gesture: {current_gesture}", 
                        (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
            progress_label = "Hold..."
        
        # Show hold progress bar
        if gesture_start_time and current_gesture != 'unknown':
            hold_time = time.time() - gesture_start_time
            progress = min(hold_time / GESTURE_HOLD_TIME, 1.0)
            
            bar_width = 200
            bar_height = 20
            filled = int(bar_width * progress)
            
            cv2.rectangle(frame, (10, 90), (10 + bar_width, 90 + bar_height), (50, 50, 50), -1)
            cv2.rectangle(frame, (10, 90), (10 + filled, 90 + bar_height), (0, 255, 0), -1)
            cv2.putText(frame, progress_label, (10, 85), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    else:
        last_gesture = None
        triggered = False
    
    if DEBUG: draw_debug_overlay(frame, recon)

    cv2.imshow("Gesture Media Controller", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break