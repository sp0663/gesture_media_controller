import cv2
from hand_tracker import HandTracker
from utils import count_extended_fingers

tracker = HandTracker()
cap = cv2.VideoCapture(0)

print("Hand tracker started! Try both hands. Press 'q' to quit.")

frame_count = 0  

while True:
    success, frame = cap.read()
    
    if not success:
        print("Failed to capture frame")
        break
    
    frame = tracker.find_hands(frame, draw=True)
    landmarks = tracker.get_landmarks(frame)
    
    if len(landmarks) > 0:
        finger_count = count_extended_fingers(landmarks)
        
        cv2.putText(frame, f"Fingers: {finger_count}", (10, 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Only print every 15 frames (about once per second at 15 FPS)
        if frame_count % 15 == 0:
            print(f"{finger_count} fingers extended")
    
    frame_count += 1  # Increment counter
    
    cv2.imshow("Hand Tracker Test", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("Test finished!")