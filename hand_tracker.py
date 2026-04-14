import cv2
import numpy as np
from openvino.runtime import Core
from collections import deque

class HandTracker:
    def __init__(self, model_path="hand_landmark.xml"):
        self.core = Core()
        self.landmark_history = deque(maxlen=5) 
        print("Compiling Hand Landmarks for Acceleration...")
        self.model = self.core.read_model(model_path)
        # Using CPU/NPU for max performance
        self.compiled_model = self.core.compile_model(self.model, "CPU")
        self.infer_request = self.compiled_model.create_infer_request()
        self.input_layer = self.compiled_model.input(0)
        self.output_layer = self.compiled_model.output(0)
        self.results = None

    def find_hands(self, frame):
        # Resize for the NPU model (256x256)
        resized = cv2.resize(frame, (256, 256))
        input_data = np.expand_dims(resized, axis=0).astype(np.float32)
        self.infer_request.infer(inputs={self.input_layer: input_data})
        self.results = self.infer_request.get_output_tensor(0).data
        return frame
    
    def get_landmarks(self, frame, hand_no=0):
        h, w, _ = frame.shape
        landmark_list = []
        if self.results is not None:
            landmarks = self.results.reshape(-1, 3)
            for id, lm in enumerate(landmarks):
                # TAMING THE 160,000: Divide by 1000, then by 256
                norm_x = (lm[0] / 1000.0) / 256.0
                norm_y = (lm[1] / 1000.0) / 256.0
                
                # Ensure they stay within 0-1 range
                norm_x = max(0, min(1, norm_x))
                norm_y = max(0, min(1, norm_y))

                cx, cy = int(norm_x * w), int(norm_y * h)
                landmark_list.append([id, cx, cy])
            
            if landmark_list:
                self.landmark_history.append(landmark_list)
                avg = np.mean(self.landmark_history, axis=0).astype(int).tolist()
                return avg, "Right"
        return [], None