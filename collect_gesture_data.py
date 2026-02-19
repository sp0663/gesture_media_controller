import cv2
import csv
import time
from hand_tracker import HandTracker

def collect_data():
    tracker = HandTracker()
    cap = cv2.VideoCapture(0)
    
    with open("gesture_data.csv", "w", newline="") as f:
        writer = csv.writer(f)
        # 42 columns for 21 landmarks (x and y)
        header = ["label"] + [f"val_{i}" for i in range(42)]
        writer.writerow(header)

        # --- PHASE 1: CUSTOM GESTURE ---
        print("Get ready to record CUSTOM gesture in 3 seconds...")
        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)
            
        print("Recording CUSTOM gesture...")
        count = 0
        while count < 100:
            success, frame = cap.read()
            frame = cv2.flip(frame, 1)
            frame = tracker.find_hands(frame)
            landmarks, _ = tracker.get_landmarks(frame)
            
            if landmarks:
                flat = []
                for lm in landmarks: flat.extend([lm[1], lm[2]])
                writer.writerow(["custom_gesture"] + flat)
                count += 1
                
                cv2.putText(frame, f"Recording Custom: {count}/100", (10, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Data Collection", frame)
            cv2.waitKey(1)

        # --- PHASE 2: BACKGROUND / NOISE ---
        print("Get ready to record BACKGROUND (move hand randomly) in 3 seconds...")
        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)
            
        print("Recording BACKGROUND...")
        count = 0
        while count < 100:
            success, frame = cap.read()
            frame = cv2.flip(frame, 1)
            frame = tracker.find_hands(frame)
            landmarks, _ = tracker.get_landmarks(frame)
            
            if landmarks:
                flat = []
                for lm in landmarks: flat.extend([lm[1], lm[2]])
                writer.writerow(["Background"] + flat)
                count += 1
                
                cv2.putText(frame, f"Recording Background: {count}/100", (10, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imshow("Data Collection", frame)
            cv2.waitKey(1)

    cap.release()
    cv2.destroyAllWindows()
    print("Data collection complete. Saved to gesture_data.csv")

if __name__ == "__main__":
    collect_data()