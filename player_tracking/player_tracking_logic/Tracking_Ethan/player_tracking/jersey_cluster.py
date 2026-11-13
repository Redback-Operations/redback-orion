from typing import Dict, List

import numpy as np

from .config import TrackingConfig
from .tracker import Track


def assign_jersey_clusters(tracks: Dict[int, Track], config: TrackingConfig) -> Dict:
    """
    Assign each track to an unsupervised jersey-colour cluster.

    This follows the JerseyColorDetection pipeline:
    1. collect torso HSV colour samples over the whole video;
    2. compute one median colour vector per player/track;
    3. standardise features;
    4. cluster players globally with KMeans.
    """
    eligible_tracks: List[Track] = []
    vectors: List[np.ndarray] = []

    for track in tracks.values():
        representative = track.representative_jersey_feature()
        if representative is None:
            continue
        if len(track.jersey_features) < config.min_samples_per_track:
            continue

        eligible_tracks.append(track)
        vectors.append(representative)

    # Default value for all tracks that cannot be clustered confidently.
    for track in tracks.values():
        track.cluster_id = None
        track.cluster_team = "Unknown"

    if not eligible_tracks:
        for track in tracks.values():
            track.apply_cluster_to_frames()
        return {
            "enabled": True,
            "status": "no_eligible_tracks",
            "requested_clusters": int(config.jersey_clusters),
            "actual_clusters": 0,
            "eligible_tracks": 0,
        }

    actual_clusters = min(int(config.jersey_clusters), len(eligible_tracks))

    if actual_clusters <= 1:
        for track in eligible_tracks:
            track.cluster_id = 0
            track.cluster_team = "Team_0"
        for track in tracks.values():
            track.apply_cluster_to_frames()
        return {
            "enabled": True,
            "status": "single_cluster_only",
            "requested_clusters": int(config.jersey_clusters),
            "actual_clusters": 1,
            "eligible_tracks": len(eligible_tracks),
        }

    try:
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
    except Exception as exc:
        raise ImportError(
            "Jersey clustering requires scikit-learn. Install it with: pip install scikit-learn"
        ) from exc

    matrix = np.stack(vectors, axis=0).astype(np.float32)
    matrix_scaled = StandardScaler().fit_transform(matrix)

    try:
        kmeans = KMeans(
            n_clusters=actual_clusters,
            random_state=int(config.kmeans_random_state),
            n_init="auto",
        )
    except TypeError:
        # Older scikit-learn versions do not support n_init="auto".
        kmeans = KMeans(
            n_clusters=actual_clusters,
            random_state=int(config.kmeans_random_state),
            n_init=10,
        )

    labels = kmeans.fit_predict(matrix_scaled)

    cluster_counts = {}
    for track, label in zip(eligible_tracks, labels):
        label = int(label)
        track.cluster_id = label
        track.cluster_team = f"Team_{label}"
        cluster_counts[str(label)] = cluster_counts.get(str(label), 0) + 1

    for track in tracks.values():
        track.apply_cluster_to_frames()

    return {
        "enabled": True,
        "status": "ok",
        "requested_clusters": int(config.jersey_clusters),
        "actual_clusters": int(actual_clusters),
        "eligible_tracks": int(len(eligible_tracks)),
        "cluster_counts": cluster_counts,
        "feature_names": [
            "median_hue",
            "median_saturation",
            "median_value",
            "red_ratio",
            "yellow_ratio",
            "blue_ratio",
            "white_ratio",
            "dark_ratio",
        ],
    }
