import cv2
import numpy as np
import csv
import os
import sys

# Hack to import HandTracker from parent folder if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from hand_tracker import HandTracker
except ImportError:
    # If running inside the subfolder and hand_tracker is there too
    from hand_tracker import HandTracker

# Setup
cap = cv2.VideoCapture(0)
tracker = HandTracker()

data = []
labels = []

# The 6 classes for the Hybrid Controller
class_map = {
    0: "Neutral",
    1: "Open Palm",
    2: "Flap UP",
    3: "Flap DOWN",
    4: "Pinch",
    5: "Fist"
}

print("=== DATA COLLECTION STARTED ===")
for k, v in class_map.items():
    print(f"Press '{k}' to record: {v}")
print("Press 'q' to Save & Quit")

while True:
    success, frame = cap.read()
    if not success: break
    
    # Mirroring matches main.py
    frame = cv2.flip(frame, 1)
    frame = tracker.find_hands(frame)
    # Get landmarks (raw list)
    landmarks_raw = tracker.get_landmarks(frame)
    
    # Handle the tuple return type if using the updated tracker
    if isinstance(landmarks_raw, tuple):
        landmarks = landmarks_raw[0]
    else:
        landmarks = landmarks_raw

    if landmarks:
        # Normalize: Wrist (point 0) becomes (0,0)
        wrist_x, wrist_y = landmarks[0][1], landmarks[0][2]
        
        normalized_row = []
        for lm in landmarks:
            normalized_row.append(lm[1] - wrist_x)
            normalized_row.append(lm[2] - wrist_y)
        
        # Check key press
        key = cv2.waitKey(1) & 0xFF
        if ord('0') <= key <= ord('5'):
            class_id = int(chr(key))
            
            # Store: [label, x0, y0, x1, y1, ... x20, y20]
            row = [class_id] + normalized_row
            data.append(row)
            
            # Visual feedback
            count = sum(1 for d in data if d[0] == class_id)
            cv2.putText(frame, f"Rec: {class_map[class_id]} ({count})", 
                       (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
    cv2.imshow("Data Collector", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

# Save to CSV
if data:
    print(f"Saving {len(data)} samples...")
    with open('gesture_data.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    print("Success! Saved to 'gesture_data.csv'")
else:
    print("No data recorded.")

cap.release()
cv2.destroyAllWindows()