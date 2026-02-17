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

def draw_debug_overlay(frame, recon):
    """
    Draws internal state of the recogniser on the frame.
    """
    h, w, _ = frame.shape
    
    # 1. DRAW SWIPE TRAIL (Yellow)
    # This visualizes the 'swipe_history' list from the recogniser
    history = list(recon.swipe_history)
    if len(history) > 1:
        for i in range(len(history) - 1):
            # Connect the dots in the history buffer
            pt1 = (int(history[i][0]), int(history[i][1]))
            pt2 = (int(history[i+1][0]), int(history[i+1][1]))
            # Draw line: Yellow, thickness increases with newer points
            cv2.line(frame, pt1, pt2, (0, 255, 255), 2) 

    # 2. DRAW STATUS PANEL (Top Right Corner)
    # Background box for readability
    cv2.rectangle(frame, (w - 220, 0), (w, 120), (0, 0, 0), -1)
    
    # Rotation Accumulator (Pink)
    # Shows how close you are to triggering a volume change
    cv2.putText(frame, f"Rot Accum: {recon.rotation_accumulator:.1f}", (w - 210, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)

    # Swipe Buffer Size (Yellow)
    # Shows how many data points are currently tracking movement
    cv2.putText(frame, f"Swipe Buffer: {len(recon.swipe_history)}", (w - 210, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    
    # Pinch Lock Status (Green/Red)
    # Shows if the system has locked onto a specific hand type
    lock_status = recon.locked_hand_type if recon.locked_hand_type else "None"
    color = (0, 255, 0) if recon.locked_hand_type else (0, 0, 255)
    cv2.putText(frame, f"Lock: {lock_status}", (w - 210, 90), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

while True:
    success, frame = cap.read()
    if not success: break
    
    # --- CHANGE MADE HERE ---
    # Flip the frame horizontally so it acts like a mirror
    # Moving hand Right physically = Moving hand Right on screen
    frame = cv2.flip(frame, 1)  
    # ------------------------

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
    
    if DEBUG: draw_debug_overlay(frame, recon)

    cv2.imshow("Gesture Media Controller", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break