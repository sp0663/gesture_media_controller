import cv2
from hand_tracker import HandTracker
import csv

def get_samples(sample, landmarks):
    wrist_x = landmarks[0][1]
    wrist_y = landmarks[0][2]
    
    for landmark in landmarks:
        relative_x = landmark[1] - wrist_x
        relative_y = landmark[2] - wrist_y
        sample.append(relative_x)
        sample.append(relative_y)


tracker = HandTracker()
cap = cv2.VideoCapture(0)
data = []
mode = None  # Current capture mode
frame_count = 0
capture_interval = 5  # Capture every 5 frames

print("Auto-Capture Data Collector")
print("P = Start pinch mode | N = Start not-pinch mode")
print("X = Stop capturing | S = Save | Q = Quit")

while True:
    success, frame = cap.read()

    if not success:
        print("Failed to capture frame")
        break

    frame = tracker.find_hands(frame, draw=True)
    landmarks = tracker.get_landmarks(frame)
    
    frame_count += 1
    
    # Auto-capture if in a mode
    if mode and len(landmarks) > 0 and frame_count % capture_interval == 0:
        sample = [mode]
        get_samples(sample, landmarks)
        data.append(sample)
    
    # Display current mode
    if mode:
        cv2.putText(frame, f"MODE: {mode.upper()} (auto-capturing)", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    else:
        cv2.putText(frame, "MODE: NONE (press P or N)", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    # Sample count
    pinch_count = sum(1 for s in data if s[0] == 'pinch')
    not_pinch_count = sum(1 for s in data if s[0] == 'not_pinch')
    cv2.putText(frame, f"Pinch: {pinch_count} | Not-Pinch: {not_pinch_count}", 
                (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
    
    cv2.putText(frame, "TIP: Move hand around!", 
                (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    cv2.imshow("Collect Data (Auto)", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('p'):
        mode = 'pinch'
        print("Started capturing PINCH")

    elif key == ord('n'):
        mode = 'not_pinch'
        print("Started capturing NOT-PINCH")
    
    elif key == ord('x'):
        mode = None
        print("Stopped capturing")

    elif key == ord('s'):
        with open('gesture_data.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)
        print(f"Saved {len(data)} samples!")
        break

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()