import pickle
import cv2
from hand_tracker import HandTracker

# Load the trained model
with open('gesture_model.pkl', 'rb') as file:
    model = pickle.load(file)

print("Model loaded successfully!")

# Setup
tracker = HandTracker()
cap = cv2.VideoCapture(0)

print("Starting live gesture recognition! Press 'q' to quit.")

while True:
    success, frame = cap.read()
    
    if not success:
        print("Failed to capture frame")
        break
    
    # Detect hand
    frame = tracker.find_hands(frame, draw=True)
    landmarks = tracker.get_landmarks(frame)
    
    # If hand detected, predict gesture
    if len(landmarks) > 0:
        # Flatten landmarks (same as training data format)
        wrist_x = landmarks[0][1]
        wrist_y = landmarks[0][2]

        flat_landmarks = []
        for lm in landmarks:
            relative_x = lm[1] - wrist_x
            relative_y = lm[2] - wrist_y
            flat_landmarks.append(relative_x)
            flat_landmarks.append(relative_y)
                
        # Get prediction probabilities
        probabilities = model.predict_proba([flat_landmarks])[0]
        prediction = model.predict([flat_landmarks])[0]
        confidence = max(probabilities)

        # Only show if confident enough
        CONFIDENCE_THRESHOLD = 0.75  # 75% confidence required

        if confidence > CONFIDENCE_THRESHOLD:
            cv2.putText(frame, f"Gesture: {prediction} ({confidence:.2f})", 
                        (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
        else:
            cv2.putText(frame, f"Uncertain ({confidence:.2f})", 
                        (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    
    # Show frame
    cv2.imshow("ML Gesture Recognition", frame)
    
    # Quit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
print("Test finished!")