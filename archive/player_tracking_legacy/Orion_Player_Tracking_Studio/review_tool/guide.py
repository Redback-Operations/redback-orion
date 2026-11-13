import tkinter as tk
from tkinter import ttk


SECTIONS = (
    ("Overview", "One place to run, inspect and share tracking work",
     "The Studio connects video tracking, problem review, team and jumper suggestions, identity correction and exports. It also displays imported movement measurements and checks camera motion. These tools help people inspect results instead of treating automatic predictions as confirmed facts.\n\n"
     "Quick demonstration: open Start and select Run sample match. In Review, play the bundled 30 second clip, select a problem timestamp, then explore Players and Results. The sample loads existing detections; it does not train a model or start a new tracking run."),
    ("Start", "Choose a new run or reopen previous work",
     "Choose video selects the source match. Choose model selects a compatible Ultralytics model and shows its supported classes. The included model detects PLAYER and REF, not club names or real player identities. Replacement models can support other classes, but no model is guaranteed to work accurately on every match.\n\n"
     "Choose ByteTrack or BoTSORT to link detections into temporary tracks. Enter a positive frame limit for a short test, or clear it for the full video. Start analysis creates a tracking CSV and annotated MP4 in app/outputs/review_runs. Progress shows processed frames. Stop finishes the current frame and preserves the partial tracking output. Each run has its own folder.\n\n"
     "Choose CSV and Load existing results open a video with its matching tracking CSV without running inference again. Common frame, track ID, class and confidence column names are accepted; visible boxes require x1, y1, x2 and y2 coordinates. Additional columns are preserved. Use the matching video, frame numbering and coordinate scale.\n\n"
     "Open saved review restores an exported review_project.json, including corrections, imported measurements, review decisions and camera results. Keep the original video available at its saved location. Export before closing or loading another project; there is no automatic review save."),
    ("Review", "Inspect the video and record decisions",
     "Use Play, Pause and the timeline slider to inspect the match. The frame indicator shows the visible box count. Missing boxes can mean no detections or that tracking did not cover that section; the coverage message helps distinguish them. A box count is not the number of players in the entire match.\n\n"
     "Problem timestamps flag short tracks, confidence drops, sudden detection count changes and possible reassociations after tracking gaps. Select a row to pause and jump to its frame, then read the explanation. Mark it Correct, False alarm or Needs review. These buttons record your assessment of the alert; they do not repair bounding boxes or retrain the model.\n\n"
     "The measurements table below the video follows the current frame. Blank entries mean no imported measurements are available there, not a measured value of zero."),
    ("Team data", "Bring matching movement results into the review",
     "In Review, Team data imports a CSV containing frame and original track ID columns plus measurements such as speed_kmh, acceleration or distance. This supports Drew's documented movement CSV format. Zone values can be preserved if supplied, but the Studio does not calculate field zones.\n\n"
     "Confirm that the file uses the same video and tracking run. Identical ID numbers from separate runs do not prove matching players. Specify the frame offset: 0 when numbering matches, or -1 when imported frames start at 1 and the loaded tracks start at 0.\n\n"
     "Every imported row must match a loaded frame and track. Duplicate or unmatched rows reject the whole import without changing existing measurements. A valid import replaces existing values with the same field names for those rows. Imported measurements stay separate from your reviewed identities and follow them into exports.\n\n"
     "Imported measurements need review. The app displays supplied values; it does not validate their physical accuracy. Camera movement, perspective and tracking errors can distort estimated speed and distance. Drew's actual output still needs an end to end compatibility check."),
    ("Camera motion", "Find sections worth inspecting",
     "In Review, Check camera motion asks how many frames to analyse from the start of the video. It estimates image translation using feature tracking and a robust transform fit, adapted from Yash Talati's diagnostic. It uses the existing video and does not need another detection model.\n\n"
     "Up to ten of the largest usable estimates appear as Camera motion entries in Problem timestamps. Select one to inspect the frame and record a review decision. Results shows the analysed frame count, usable estimates and mean image translation in pixels per frame. Stop can end this check early; the partial coverage is reported.\n\n"
     "These are relative review candidates, not confirmed camera cuts or tracking errors. Failed estimates are not counted as zero motion. The check does not stabilise the video, correct player positions or convert pixels to metres. A repeated check replaces the previous camera results while retaining decisions for matching camera event frames."),
    ("Players", "Review labels and reconnect track fragments",
     "Select a track to see its class, team, jumper, identity and detection count. Selection also seeks the video to its first frame. Edit Team and Jumper number, then Save correction. These corrections affect review labels and exports, not the trained model.\n\n"
     "Suggest teams from colours examines several player crops. Read jumper numbers uses OCR across crops. Both are suggestions requiring review, especially with similar uniforms, shadows, distant players or blur. Existing assigned team and jumper values are preserved by the suggestion actions. Crops are stored in app/outputs/review_crops.\n\n"
     "Matching reviewed teams and jumper numbers can group nonoverlapping tracks. For a manual merge, select multiple tracks, enter an identity under Merge selected tracks as, then select Merge selected tracks. Overlapping frame ranges are rejected, including conflicts with an existing manual group. Original track IDs remain available.\n\n"
     "An identity group is a review decision, not proof of a real person's identity. Check the video before merging. Corrections do not rewrite the previously generated annotated MP4; use the live review display and exported review data to show them."),
    ("Results", "Save a complete review handoff",
     "Results summarises temporary tracks, identity groups, problem timestamps and reviewed issues. These counts describe this run and its review, not detection accuracy or the total match squad.\n\n"
     "Export results writes four files into your chosen folder:\n\n"
     "reviewed_tracks.csv: per track summaries, reviewed team and jumper values, and identity groups.\n"
     "review_events.csv: flagged timestamps and your review decisions.\n"
     "reviewed_detections.csv: per frame detections and identity groups, plus supplied measurements with imported_ column prefixes.\n"
     "review_project.json: detections, corrections, decisions, import source details and camera estimates for reopening.\n\n"
     "Choose a new export folder to retain older versions; exporting into the same folder replaces those filenames. The JSON refers to the original video rather than embedding it. The tracking MP4 is saved separately in the run folder. Wait for background actions to finish before exporting."),
    ("Project contribution", "Integration, review logic and a usable handoff",
     "Sahan Chandimal's Studio contribution includes the desktop interface, connected review workflow, editable identity handling, overlap protection, compatible data import, saved review restoration, exports, validation and runnable packaging. The interface makes those capabilities accessible; it is not the only contribution.\n\n"
     "The detection models, ByteTrack, BoTSORT and OCR engines are existing tools. Team contributions supply tracking, colour analysis, crops, diagnostics and movement formats. The Studio connects and adapts that work rather than claiming those algorithms as new inventions. Open Credits for the contributors and connected areas.\n\n"
     "The latest local additions are separate from the first merged Studio version. Test results demonstrate specific tested workflows, not perfect performance on every video. Human review remains part of the process."),
)


def build_guide(parent, notebook, destinations):
    toolbar = ttk.Frame(parent)
    toolbar.pack(fill="x", pady=(0, 12))
    ttk.Label(toolbar, text="Guide", font=("Arial", 20, "bold")).pack(side="left", padx=(0, 16))
    selector = ttk.Combobox(toolbar, values=[item[0] for item in SECTIONS], state="readonly", width=24)
    selector.current(0)
    selector.pack(side="left")
    for name, destination in destinations.items():
        ttk.Button(toolbar, text=f"Open {name}", command=lambda tab=destination: notebook.select(tab)).pack(side="left", padx=4)
    container = ttk.Frame(parent)
    container.pack(fill="both", expand=True)
    body = tk.Text(container, wrap="word", font=("Arial", 12), background="white", foreground="#172033",
                   relief="flat", padx=22, pady=18, spacing1=3, spacing3=10)
    scroll = ttk.Scrollbar(container, orient="vertical", command=body.yview)
    body.configure(yscrollcommand=scroll.set)
    scroll.pack(side="right", fill="y")
    body.pack(side="left", fill="both", expand=True)
    body.tag_configure("heading", font=("Arial", 17, "bold"), foreground="#287568", spacing1=18, spacing3=10)
    marks = {}
    for name, title, content in SECTIONS:
        marks[name] = body.index("end-1c")
        body.insert("end", f"{name}: {title}\n", "heading")
        body.insert("end", content + "\n\n")
    body.configure(state="disabled")
    selector.bind("<<ComboboxSelected>>", lambda event: body.yview(marks[selector.get()]))
    return body, selector
