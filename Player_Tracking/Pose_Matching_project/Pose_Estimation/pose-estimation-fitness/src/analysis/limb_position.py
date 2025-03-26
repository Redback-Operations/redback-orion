import numpy as np

def evaluate_limb_positions(landmarks, exercise_type):
    """
    Evaluate limb positions based on pose landmarks during a specified exercise.
    
    Parameters:
    landmarks (np.ndarray): Array of shape (N, 2) containing the (x, y) coordinates of key points.
    exercise_type (str): The type of exercise being performed (e.g., 'deadlift', 'bench press').
    
    Returns:
    dict: A dictionary containing evaluation results and suggested corrections.
    """
    results = {}
    
    # Ensure required keypoints exist
    required_indices = [11, 12, 14] if exercise_type == 'deadlift' else [10, 11, 12]
    if not all(idx < len(landmarks) and landmarks[idx] is not None for idx in required_indices):
        results['error'] = "Insufficient keypoints for evaluation."
        return results

    if exercise_type == 'deadlift':
        # Example evaluation for deadlift
        hip_angle = calculate_angle(landmarks[11], landmarks[12], landmarks[14])  # Example indices for hip
        knee_angle = calculate_angle(landmarks[12], landmarks[14], landmarks[16])  # Example indices for knee
        
        results['hip_angle'] = hip_angle
        results['knee_angle'] = knee_angle
        
        if hip_angle < 160:
            results['hip_correction'] = "Increase hip hinge to avoid back strain."
        else:
            results['hip_correction'] = "Hip position is optimal."
        
        if knee_angle > 170:
            results['knee_correction'] = "Bend knees more to maintain proper form."
        else:
            results['knee_correction'] = "Knee position is optimal."
    
    elif exercise_type == 'bench press':
        # Example evaluation for bench press
        elbow_angle = calculate_angle(landmarks[10], landmarks[11], landmarks[12])  # Example indices for elbow
        shoulder_angle = calculate_angle(landmarks[8], landmarks[10], landmarks[12])  # Example indices for shoulder
        
        results['elbow_angle'] = elbow_angle
        results['shoulder_angle'] = shoulder_angle
        
        if elbow_angle < 90:
            results['elbow_correction'] = "Elbows should be at a 90-degree angle for safety."
        else:
            results['elbow_correction'] = "Elbow position is optimal."
        
        if shoulder_angle > 180:
            results['shoulder_correction'] = "Lower shoulders to avoid strain."
        else:
            results['shoulder_correction'] = "Shoulder position is optimal."
    
    return results

def calculate_angle(point_a, point_b, point_c):
    """
    Calculate the angle between three points.
    
    Parameters:
    point_a (tuple): Coordinates of the first point (x, y).
    point_b (tuple): Coordinates of the second point (x, y).
    point_c (tuple): Coordinates of the third point (x, y).
    
    Returns:
    float: The angle in degrees.
    """
    a = np.array(point_a)
    b = np.array(point_b)
    c = np.array(point_c)
    
    ba = a - b
    bc = c - b
    
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))  # Clip to avoid numerical errors
    return np.degrees(angle)

def calculate_strain(landmarks, exercise_type):
    """
    Calculate strain based on joint angles and deviations from optimal form.

    Parameters:
    landmarks (np.ndarray): Array of shape (N, 2) containing the (x, y) coordinates of key points.
    exercise_type (str): The type of exercise being performed (e.g., 'deadlift', 'bench press').

    Returns:
    dict: A dictionary containing strain metrics and detailed explanations.
    """
    strain_results = {}

    if exercise_type == 'deadlift':
        # Example: Calculate strain on the lower back
        hip_angle = calculate_angle(landmarks[11], landmarks[12], landmarks[14])  # Hip angle
        knee_angle = calculate_angle(landmarks[12], landmarks[14], landmarks[16])  # Knee angle

        strain_results['hip_angle'] = hip_angle
        strain_results['knee_angle'] = knee_angle

        # Check if hips are straight across
        if abs(landmarks[11][1] - landmarks[12][1]) > 10:  # Allowable y-coordinate difference
            strain_results['hip_alignment'] = (
                "Hips are not straight across. Ensure the left and right hips are level."
            )
        else:
            strain_results['hip_alignment'] = "Hips are straight across."

        # Check if back is straight
        back_angle = calculate_angle(landmarks[1], landmarks[12], landmarks[11])  # Neck to spine to hips
        strain_results['back_angle'] = back_angle
        if back_angle < 160 or back_angle > 180:
            strain_results['back_straightness'] = (
                "Back is not straight. Ensure the back is aligned and avoid rounding."
            )
        else:
            strain_results['back_straightness'] = "Back is straight."

        # Check if knees are bent
        if knee_angle > 170:
            strain_results['knee_bend'] = (
                "Knees are not bent enough. Bend the knees slightly to maintain proper form."
            )
        else:
            strain_results['knee_bend'] = "Knees are bent properly."

    elif exercise_type == 'bench press':
        # Example: Calculate strain on shoulders
        elbow_angle = calculate_angle(landmarks[10], landmarks[11], landmarks[12])  # Elbow angle
        shoulder_angle = calculate_angle(landmarks[8], landmarks[10], landmarks[12])  # Shoulder angle

        strain_results['elbow_angle'] = elbow_angle
        strain_results['shoulder_angle'] = shoulder_angle

        if elbow_angle < 90:
            strain_results['elbow_strain'] = (
                "High strain on elbows. The elbow angle is too small, indicating excessive bending. "
                "This can lead to joint stress and reduced stability. Adjust arm position to achieve a 90-degree angle."
            )
        else:
            strain_results['elbow_strain'] = "Elbow strain is minimal. The elbow angle is within the optimal range."

        if shoulder_angle > 180:
            strain_results['shoulder_strain'] = (
                "High strain on shoulders. The shoulder angle is too large, indicating overextension. "
                "This can cause shoulder impingement or discomfort. Lower the shoulders to reduce strain."
            )
        else:
            strain_results['shoulder_strain'] = "Shoulder strain is minimal. The shoulder angle is within the optimal range."

    return strain_results