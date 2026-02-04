import csv
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle

# Load data
with open('gesture_data.csv', 'r') as file:
    reader = csv.reader(file)
    data = list(reader)
    X = []  
    y = []  
    
    for row in data:
        y.append(row[0])
        X.append([int(coord) for coord in row[1:]])

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"Training samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")
print(f"Pinch samples: {y.count('pinch')}")
print(f"Not-pinch samples: {y.count('not_pinch')}")
print()

# Train Random Forest
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

print(f"Model Accuracy: {accuracy * 100:.2f}%")

# Save the model
with open('pinch_model.pkl', 'wb') as file:
    pickle.dump(model, file)

print("Model saved as pinch_model.pkl")