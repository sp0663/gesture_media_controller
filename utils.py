import numpy as np

def cal_distance(point1, point2):

    p1 = np.array([point1[1], point1[2]])
    p2 = np.array([point2[1], point2[2]])
    
    return np.linalg.norm(p1 - p2)


def cal_angle(point1, point2, point3):

    p1 = np.array([point1[1], point1[2]])
    p2 = np.array([point2[1], point2[2]])
    p3 = np.array([point3[1], point3[2]])

    v1 = p1 - p2
    v2 = p3 - p2

    cosine = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    return np.degrees(np.arccos(cosine))

def finger_extended(landmarks, finger_tip_id):

    mcp, pcp, tip = landmarks[finger_tip_id - 3], landmarks[finger_tip_id - 2], landmarks[finger_tip_id]
    angle1 = cal_angle(mcp, pcp, tip)

    return (angle1 > 160)
    

def count_extended_fingers(landmarks):

    count = 0
    finger_tip_id = [4, 8, 12, 16, 20]
    
    for id in finger_tip_id:
        if finger_extended(landmarks, id):
            count += 1
    
    return count