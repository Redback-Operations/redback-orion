# Team Classification Methods Comparison

## 1. Objective

This evaluation compares two existing team-colour classification methods in the Orion player-tracking system:

- Method A: JerseyColorDetection (`color_detection_cli.py`).

- Method B: Studio team classification (`suggest_teams`).

The objective is to examine classification agreement, prediction coverage, umpire handling and practical limitations without modifying either existing classification algorithm.

## 2. Evaluation Environment

| Component | Configuration |
|---|---|
| Operating system | Windows |
| Python | 3.11 |
| Tracking model | player_ref_best.pt |
| Repository | Redback-Operations/redback-orion |
| Evaluation script | evaluation/compare_team_methods.py |
| Base commit | ab27b1a |

## 3. Evaluation Dataset

The evaluation was conducted using the supplied video.

| Property | Value |
|---|---|
| Clip | team_clip_1.mp4 |
| Apparent match | Carlton vs Gold Coast Suns |
| Clip-relative timestamps | 00:00–00:17.25 |
| Duration | 17.25 seconds |
| Resolution | 384 × 848 pixels |
| Frame rate | Approximately 59.92 FPS |
| Total frames | 1,034 |
| Detection records | 54 |
| Unique track IDs | 7 |
| Repeated-detection tracks | 3 |
| Single-frame tracks | 4 |

The supplied footage appears to be a mobile screen recording of an already annotated player-tracking video. The original broadcast date and match timestamps could not be independently verified.

The original evaluation scope requested three clips from different matches. Only one available clip was evaluated in this experiment.

## 4. Classification Methods

### 4.1 Method A: JerseyColorDetection

Source:

`analysis_pipeline/identify_players/color_detection_cli.py`

Method A extracts torso colour features from tracked players using HSV colour information and additional colour-distribution features.

Representative track features are clustered using KMeans with three clusters and a random state of 42.

The method assigned three repeated-detection tracks to three different clusters.

### 4.2 Method B: Studio Team Classification

Source:

`orion_player_tracking_studio/review_tool/vision.py`

Function:

`suggest_teams`

Method B extracts torso regions from player crop images and calculates representative median HSV colour features.

It uses KMeans with two clusters and a random state of 42 when sufficient feature vectors are available.

The method explicitly excludes tracks classified as REF, REFEREE or UMPIRE.

## 5. Reference Labelling

Reference labels were established through manual inspection of player crops and full-frame screenshots. Existing annotations visible in the supplied footage were used as supporting evidence.

| Track ID | Detection records | Detector class | Reference label |
|---|---:|---|---|
| 3 | 12 | PLAYER | Gold Coast Suns |
| 5 | 25 | REF | umpire |
| 6 | 13 | PLAYER | unknown |

Tracks 1, 2, 4 and 7 were excluded from reference scoring because each contained only one detection record.

Track 6 was excluded from accuracy calculations because overlapping subjects and inconsistent visual evidence prevented reliable team identification.

These reference labels are manually reviewed but have not been independently validated against original match footage.

## 6. Evaluation Methodology

The comparison script performs the following operations:

1\. Loads reference team labels from the evaluation CSV.

2\. Reads Method A predictions from the generated metrics CSV.

3\. Loads existing player tracking records.

4\. Extracts player crops using the existing Studio implementation.

5\. Executes Method B using the existing suggest_teams function.

6\. Maps predicted clusters to reference labels using majority voting.

7\. Calculates prediction coverage and mapped agreement.

8\. Reports missing predictions and umpire handling.

9\. Excludes unverified reference labels from scoring.

Player-only results are reported separately from Method A's umpire-inclusive results.

Majority mapping and scoring use the same labelled tracks. Therefore, the reported agreement is descriptive and does not represent independent test-set accuracy.

## 7. Experimental Results

### 7.1 Raw Predictions

| Track ID | Reference label | Method A | Method B |
|---|---|---|---|
| 3 | Gold Coast Suns | Cluster_1 | Team 1 |
| 5 | umpire | Cluster_0 | Excluded |
| 6 | unknown | Cluster_2 | Team 1 |

### 7.2 Prediction Coverage

| Metric | Method A | Method B |
|---|---:|---:|
| Repeated-detection tracks | 3 | 3 |
| Classified tracks | 3 | 2 |
| Prediction coverage | 100.00% | 66.67% |

Method B's lower overall coverage results from its intentional exclusion of the umpire.

### 7.3 Player-Only Evaluation

| Metric | Method A | Method B |
|---|---:|---:|
| Eligible labelled player tracks | 1 | 1 |
| Classified tracks | 1 | 1 |
| Correct mapped predictions | 1 | 1 |
| Missing predictions | 0 | 0 |
| Prediction coverage | 100.00% | 100.00% |
| Mapped agreement | 100.00% | 100.00% |

Both methods achieved complete mapped agreement on the single labelled player.

However, because only one labelled player was available and the same label was used for majority mapping, these results cannot establish general classification accuracy or demonstrate that either method is superior.

### 7.4 Method A Including Umpires

| Metric | Result |
|---|---:|
| Eligible reference tracks | 2 |
| Classified tracks | 2 |
| Correct mapped predictions | 2 |
| Prediction coverage | 100.00% |
| Mapped agreement | 100.00% |

Method A assigned the umpire to Cluster_0, which was subsequently mapped to the umpire reference label.

This demonstrates the observed grouping behaviour on this clip, rather than independently validated umpire recognition accuracy.

## 8. Failure Analysis

### 8.1 Low-Resolution Input

The supplied footage has a resolution of 384 × 848 pixels. The actual match occupies only part of the video frame.

Small player bounding boxes reduce the reliability of extracted jersey colour information.

### 8.2 Existing Video Annotations

The input contains previously generated bounding boxes, class labels and confidence scores. These overlays may interfere with detection and colour-feature extraction.

### 8.3 Sparse Player Tracking

Only 54 detection records were generated across 1,034 source frames.

Four of the seven track IDs appeared only once, significantly reducing the available evaluation sample.

### 8.4 Ambiguous Player Identity

Track 6 showed inconsistent visual evidence and overlapping subjects.

Its actual team could not be reliably established, so it was excluded from reference scoring.

### 8.5 Umpire Handling

Method B excluded track 5 because its detector class was REF.

All five crop images for this track were readable and contained valid torso regions. Therefore, the missing prediction was intentional behaviour rather than a crop extraction failure.

### 8.6 Over-Clustering

Method A generated three clusters from three valid tracks.

With such a small sample, each track can occupy a separate cluster. Majority mapping can consequently produce misleadingly high agreement.

### 8.7 Unrelated Pipeline Failure

The workload heatmap stage returned a subprocess error during full pipeline execution.

The team classification stage completed successfully. The workload failure was outside the scope of this comparison and was not modified.

## 9. Recommendation

Method B is provisionally preferable for player-only team grouping when referee classifications are reliable, because it explicitly excludes officials and uses two team clusters.

Method A remains useful when the application requires an additional cluster that may represent officials or another visually distinct group.

However, neither method can be recommended as definitively more accurate based on this experiment. A larger dataset containing independently labelled players from both teams and multiple matches is required.

## 10. Reproducing the Evaluation

Run the following commands from the player_tracking directory using the configured Python environment.

Generate tracking and Method A classification results:

```bash

python analysis_pipeline/run_pipeline.py data/videos/team_clip_1.mp4

```

Run the comparison:

```bash

python evaluation/compare_team_methods.py team_clip_1

```

Validate Python syntax:

```bash

python -m py_compile evaluation/compare_team_methods.py

```

The comparison script also supports multiple prepared clips supplied as command-line arguments.

## 11. Conclusion

Both existing classification methods were successfully executed and compared without modifying their implementations.

The experiment demonstrated differences in clustering behaviour, prediction coverage and umpire exclusion.

The results also highlighted the importance of suitable source footage, reliable player tracking and sufficiently large reference datasets.

The single-clip evaluation provides preliminary technical evidence but does not establish comparative generalisation accuracy.

## 12. Automated Testing and Validation

The existing project test suites were executed on Windows using Python 3.11 and pytest 9.2.0.

| Test Suite | Passed | Failed |
|---|---:|---:|
| Player Service | 6 | 0 |
| Analysis Pipeline | 11 | 0 |
| Evaluation | 4 | 0 |
| Training | 7 | 1 |
| Total | 28 | 1 |

The overall test pass rate was 96.55%.

### 12.1 Comparison Script Validation

The new comparison script was successfully executed using the supplied evaluation clip.

Python syntax validation also completed successfully using py_compile.

### 12.2 Existing Windows Compatibility Issue

The following existing training test failed:

`DatasetIntegrityTests.test_fine_tune_preserves_checkpoint_classes_and_explicit_learning_rate`

Location:

`training/tests/test_dataset_integrity.py:77`

The test expects a checkpoint path ending with `models/player_ref_best.pt`. However, Windows generates the corresponding path using backslashes.

A separate diagnostic confirmed that the original string assertion returns False, while normalising the path separators makes the assertion return True.

Git verification confirmed that neither the training implementation nor its corresponding test was modified during this evaluation.

The issue was left unchanged because training functionality is outside the assigned team-classification comparison scope.

### 12.3 Implementation Scope

Neither existing team-classification algorithm was modified. The implementation introduces a standalone comparison script, reference labels and technical documentation.

The comparison script passed its execution and syntax checks. Dedicated automated unit tests for the new comparison script have not been added.

### 12.4 Manual API Integration Testing

The Player Tracking API was manually tested through the FastAPI Swagger interface.

| Parameter | Result |
|---|---|
| Endpoint | POST /tracking |
| Input video | team_clip_1.mp4 |
| HTTP response | 200 OK |
| Response format | JSON |
| Video duration | 17.255 seconds |
| Total source frames | 1,034 |
| Resolution | 384 × 848 pixels |
| Test status | Passed |

The API successfully returned structured tracking results containing frame numbers, timestamps, player IDs, detector classes, bounding-box coordinates and confidence scores.

The successful response confirms that the existing player-tracking API is operational in the configured Windows environment. This functionality test does not establish detection or team-classification accuracy.
