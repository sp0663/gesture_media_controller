import csv
import pickle
from sklearn.neighbors import KNeighborsClassifier

def train():
    X, y = [], []
    try:
        with open("gesture_data.csv", "r") as f:
            reader = csv.reader(f)
            next(reader) # Skip header
            for row in reader:
                y.append(row[0]) # Label
                X.append([float(val) for val in row[1:]]) # Coordinates
    except FileNotFoundError:
        print("No gesture_data.csv found. Please run collection first.")
        return

    # Train a KNN model (K=3 is perfect for simple geometric data)
    model = KNeighborsClassifier(n_neighbors=3)
    model.fit(X, y)

    # Save the model
    with open("gesture_model.pkl", "wb") as f:
        pickle.dump(model, f)
    
    print("Model successfully trained and saved to gesture_model.pkl")

if __name__ == "__main__":
    train()