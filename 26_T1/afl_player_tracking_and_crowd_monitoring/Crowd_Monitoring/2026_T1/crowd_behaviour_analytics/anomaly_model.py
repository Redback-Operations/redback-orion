"""IsolationForest-based anomaly scoring for tracked crowd behaviour."""

from math import sqrt

import numpy as np
from sklearn.ensemble import IsolationForest


def _track_feature_vector(track_id, history):
    speeds = [entry.get("speed", 0.0) for entry in history]
    normalized_speeds = [entry.get("normalized_speed", 0.0) for entry in history]
    first_centroid = history[0].get("centroid", [0.0, 0.0])
    last_centroid = history[-1].get("centroid", [0.0, 0.0])
    dx = float(last_centroid[0]) - float(first_centroid[0])
    dy = float(last_centroid[1]) - float(first_centroid[1])
    displacement = sqrt(dx * dx + dy * dy)
    avg_height = max(
        sum(entry.get("bbox_height", 1.0) for entry in history) / max(len(history), 1),
        1.0,
    )
    normalized_displacement = displacement / avg_height

    return {
        "track_id": track_id,
        "vector": [
            float(len(history)),
            float(sum(normalized_speeds) / len(normalized_speeds)) if normalized_speeds else 0.0,
            float(max(normalized_speeds, default=0.0)),
            float(normalized_displacement),
            float(sum(speeds) / len(speeds)) if speeds else 0.0,
        ],
    }


def detect_track_anomalies(track_histories):
    """Score tracked people using IsolationForest and return anomalous tracks."""
    if not track_histories:
        return {
            "model_enabled": False,
            "anomaly_track_ids": [],
            "running_track_ids": [],
            "anomaly_count": 0,
            "track_scores": [],
        }

    track_vectors = [
        _track_feature_vector(track_id, history)
        for track_id, history in track_histories.items()
        if history
    ]

    if not track_vectors:
        return {
            "model_enabled": False,
            "anomaly_track_ids": [],
            "running_track_ids": [],
            "anomaly_count": 0,
            "track_scores": [],
        }

    # Synthetic reference samples represent relatively normal crowd motion.
    reference_vectors = np.array(
        [
            [2.0, 0.05, 0.10, 0.12, 1.5],
            [3.0, 0.08, 0.14, 0.20, 2.0],
            [4.0, 0.12, 0.22, 0.30, 2.7],
            [5.0, 0.18, 0.30, 0.45, 3.5],
            [4.0, 0.10, 0.18, 0.25, 2.3],
            [5.0, 0.16, 0.28, 0.38, 3.2],
            [6.0, 0.22, 0.36, 0.55, 4.0],
            [7.0, 0.28, 0.42, 0.72, 5.0],
        ],
        dtype=float,
    )
    observed_vectors = np.array([entry["vector"] for entry in track_vectors], dtype=float)
    training_vectors = np.vstack([reference_vectors, observed_vectors])

    model = IsolationForest(
        n_estimators=100,
        contamination=0.15,
        random_state=42,
    )
    model.fit(training_vectors)

    predictions = model.predict(observed_vectors)
    scores = model.decision_function(observed_vectors)

    anomaly_track_ids = []
    running_track_ids = []
    track_scores = []

    for track_entry, prediction, score in zip(track_vectors, predictions, scores):
        track_id = track_entry["track_id"]
        history_length, avg_normalized_speed, max_normalized_speed, normalized_displacement, avg_speed = track_entry["vector"]
        is_anomaly = int(prediction) == -1
        anomaly_score = round(float(-score), 4)

        if is_anomaly:
            anomaly_track_ids.append(track_id)

        if (
            is_anomaly
            and history_length >= 3
            and avg_normalized_speed >= 0.55
            and max_normalized_speed >= 0.9
            and normalized_displacement >= 1.0
        ):
            running_track_ids.append(track_id)

        track_scores.append(
            {
                "track_id": track_id,
                "history_length": int(history_length),
                "avg_speed": round(avg_speed, 2),
                "avg_normalized_speed": round(avg_normalized_speed, 4),
                "max_normalized_speed": round(max_normalized_speed, 4),
                "normalized_displacement": round(normalized_displacement, 4),
                "anomaly_score": anomaly_score,
                "is_anomaly": is_anomaly,
            }
        )

    return {
        "model_enabled": True,
        "anomaly_track_ids": anomaly_track_ids,
        "running_track_ids": running_track_ids,
        "anomaly_count": len(anomaly_track_ids),
        "track_scores": track_scores,
    }
