import numpy as np

# This file is used to analyze limb positions and strain during exercises
# This file will need to be modified or rewritten to implement the new model
# Currently its accuracy is not sufficient


def evaluate_limb_positions(landmarks, exercise_type):
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
    # Calculate the angle between three points
    ba = point_a - point_b
    bc = point_c - point_b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)

def calculate_midpoint(point_a, point_b):
    return (point_a + point_b) / 2

def calculate_strain(landmarks, exercise_type):
    strain_results = {}

    if exercise_type == 'deadlift':
        # Example: Calculate strain on the lower back
        hip_angle = calculate_angle(landmarks[11], landmarks[12], landmarks[14])  # Hip angle
        knee_angle = calculate_angle(landmarks[12], landmarks[14], landmarks[16])  # Knee angle

        strain_results['hip_angle'] = hip_angle
        strain_results['knee_angle'] = knee_angle

        # Debugging statements to verify calculations
        print(f"Debug: Hip angle = {hip_angle}")
        print(f"Debug: Knee angle = {knee_angle}")

        # Calculate the midpoint of the back (spine)
        back_midpoint = calculate_midpoint(landmarks[1], landmarks[12])  # Neck to spine midpoint
        back_angle = calculate_angle(landmarks[1], back_midpoint, landmarks[12])  # Neck to midpoint to spine

        strain_results['back_angle'] = back_angle
        print(f"Debug: Back angle = {back_angle}")

        # Provide feedback based on the back angle
        if back_angle < 120:
            strain_results['back_alignment'] = (
                "Back angle is too low (poor form). Straighten your back to improve alignment."
            )
        elif 120 <= back_angle < 170:
            strain_results['back_alignment'] = (
                "Back angle is acceptable but could be improved. Aim for a straighter back."
            )
        elif 170 <= back_angle <= 190:
            strain_results['back_alignment'] = "Back angle is ideal. Great form!"
        else:
            strain_results['back_alignment'] = (
                "Back angle is too high (overextension). Avoid arching your back excessively."
            )

    elif exercise_type == 'bench press':
        # Example: Calculate strain on shoulders
        elbow_angle = calculate_angle(landmarks[10], landmarks[11], landmarks[12])  # Elbow angle
        shoulder_angle = calculate_angle(landmarks[8], landmarks[10], landmarks[12])  # Shoulder angle

        strain_results['elbow_angle'] = elbow_angle
        strain_results['shoulder_angle'] = shoulder_angle

        # Debugging statements for bench press
        print(f"Debug: Elbow angle = {elbow_angle}")
        print(f"Debug: Shoulder angle = {shoulder_angle}")

        if elbow_angle < 90:
            strain_results['elbow_strain'] = (
                "High strain on elbows. The elbow angle is too small, indicating excessive bending."
            )
        else:
            strain_results['elbow_strain'] = "Elbow strain is minimal."

        if shoulder_angle > 180:
            strain_results['shoulder_strain'] = (
                "High strain on shoulders. The shoulder angle is too large, indicating overextension."
            )
        else:
            strain_results['shoulder_strain'] = "Shoulder strain is minimal."

    elif exercise_type == 'squat':
        # Example: Calculate strain for squats
        hip_angle = calculate_angle(landmarks[11], landmarks[12], landmarks[14])  # Hip angle
        knee_angle = calculate_angle(landmarks[12], landmarks[14], landmarks[16])  # Knee angle

        strain_results['hip_angle'] = hip_angle
        strain_results['knee_angle'] = knee_angle

        # Debugging statements to verify calculations
        print(f"Debug: Hip angle = {hip_angle}")
        print(f"Debug: Knee angle = {knee_angle}")

        # Provide feedback for squats
        if hip_angle < 90:
            strain_results['hip_alignment'] = (
                "Hip angle is too low. Ensure proper depth without excessive bending."
            )
        elif 90 <= hip_angle <= 120:
            strain_results['hip_alignment'] = "Hip angle is ideal. Great form!"
        else:
            strain_results['hip_alignment'] = (
                "Hip angle is too high. Lower your hips to achieve proper squat depth."
            )

        if knee_angle < 90:
            strain_results['knee_alignment'] = (
                "Knee angle is too low. Ensure proper alignment without excessive bending."
            )
        elif 90 <= knee_angle <= 120:
            strain_results['knee_alignment'] = "Knee angle is ideal. Great form!"
        else:
            strain_results['knee_alignment'] = (
                "Knee angle is too high. Bend your knees more to achieve proper squat depth."
            )

        # Calculate the midpoint of the back (spine)
        back_midpoint = calculate_midpoint(landmarks[1], landmarks[12])  # Neck to spine midpoint
        back_angle = calculate_angle(landmarks[1], back_midpoint, landmarks[12])  # Neck to midpoint to spine

        strain_results['back_angle'] = back_angle
        print(f"Debug: Back angle = {back_angle}")

        # Provide feedback based on the back angle
        if back_angle < 120:
            strain_results['back_alignment'] = (
                "Back angle is too low (poor form). Straighten your back to improve alignment."
            )
        elif 120 <= back_angle < 170:
            strain_results['back_alignment'] = (
                "Back angle is acceptable but could be improved. Aim for a straighter back."
            )
        elif 170 <= back_angle <= 190:
            strain_results['back_alignment'] = "Back angle is ideal. Great form!"
        else:
            strain_results['back_alignment'] = (
                "Back angle is too high (overextension). Avoid arching your back excessively."
            )

    return strain_results