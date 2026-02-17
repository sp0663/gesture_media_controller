import csv
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

print("--------------------------")
print("Loading gesture_data.csv...")

X = []
y = []

try:
    with open('gesture_data.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if not row: continue # Skip empty lines
            # Row format: [label, x0, y0, ... x20, y20]
            # row[0] is the Class
            # ID (0-5)
            y.append(int(row[0]))
            # row[1:] are the 42 coordinates
            X.append([float(x) for x in row[1:]])
except FileNotFoundError:
    print("ERROR: 'gesture_data.csv' not found.")
    print("Make sure you saved it by pressing 's' in the collection script!")
    exit()

print(f"Loaded {len(X)} samples.")

# Split Data (80% for training, 20% for testing)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

print("Training Random Forest Model...")
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Test Accuracy
preds = model.predict(X_test)
acc = accuracy_score(y_test, preds)
print(f"Model Accuracy: {acc*100:.2f}%")

# Save the Brain
with open('gesture_model.pkl', 'wb') as f:
    pickle.dump(model, f)
print("SUCCESS: Model saved to 'gesture_model.pkl'")
print("--------------------------")