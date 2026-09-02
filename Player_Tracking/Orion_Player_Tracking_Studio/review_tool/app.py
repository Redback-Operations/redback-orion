from __future__ import annotations

import queue
import threading
import tkinter as tk
from collections import defaultdict
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .core import ReviewProject, TrackRow, find_review_events, run_ocr
from .tracking import inspect_model, track_video
from .vision import extract_track_crops, suggest_teams


ROOT = Path(__file__).resolve().parent.parent
ACCENT = "#2f6fed"
NAVY = "#172033"
PALE = "#f4f7fb"
MUTED = "#64748b"


class VideoPanel(ttk.Frame):
    def __init__(self, parent: tk.Widget, on_frame=None) -> None:
        super().__init__(parent)
        self.on_frame = on_frame
        self.path = ""
        self.capture = None
        self.playing = False
        self.fps = 25.0
        self.total = 0
        self.rows_by_frame: dict[int, list[TrackRow]] = {}
        self.image_ref = None
        self.updating_scale = False

        self.canvas = tk.Canvas(self, background="#0b1020", highlightthickness=0, height=470)
        self.canvas.pack(fill="both", expand=True)
        controls = ttk.Frame(self)
        controls.pack(fill="x", pady=(8, 0))
        self.play_button = ttk.Button(controls, text="Play", command=self.toggle, width=9)
        self.play_button.pack(side="left")
        self.scale = ttk.Scale(controls, from_=0, to=1, command=self._seek_from_scale)
        self.scale.pack(side="left", fill="x", expand=True, padx=10)
        self.time_label = ttk.Label(controls, text="00:00 / 00:00")
        self.time_label.pack(side="right")

    def load(self, path: str, rows: list[TrackRow], fps: float | None = None) -> None:
        try:
            import cv2
        except ImportError as exc:
            messagebox.showerror("Video unavailable", "OpenCV is needed to play video inside the app.")
            raise exc
        if self.capture:
            self.capture.release()
        self.path = path
        self.capture = cv2.VideoCapture(path)
        self.fps = fps or self.capture.get(cv2.CAP_PROP_FPS) or 25
        self.total = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.scale.configure(to=max(1, self.total - 1))
        grouped: defaultdict[int, list[TrackRow]] = defaultdict(list)
        for row in rows:
            grouped[row.frame].append(row)
        self.rows_by_frame = dict(grouped)
        self.show_frame(0)

    def show_frame(self, frame_number: int) -> None:
        if not self.capture:
            return
        import cv2
        from PIL import Image, ImageTk

        frame_number = max(0, min(int(frame_number), max(0, self.total - 1)))
        self.capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ok, frame = self.capture.read()
        if not ok:
            return
        for row in self.rows_by_frame.get(frame_number, []):
            x1, y1, x2, y2 = map(int, (row.x1, row.y1, row.x2, row.y2))
            cv2.rectangle(frame, (x1, y1), (x2, y2), (50, 220, 120), 2)
            cv2.putText(frame, f"{row.class_name} {row.track_id}", (x1, max(18, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (50, 220, 120), 2)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)
        canvas_width = max(640, self.canvas.winfo_width())
        canvas_height = max(360, self.canvas.winfo_height())
        image.thumbnail((canvas_width, canvas_height))
        self.image_ref = ImageTk.PhotoImage(image)
        self.canvas.delete("all")
        self.canvas.create_image(canvas_width // 2, canvas_height // 2, image=self.image_ref, anchor="center")
        self.updating_scale = True
        self.scale.set(frame_number)
        self.updating_scale = False
        self.time_label.configure(text=f"{self._time(frame_number)} / {self._time(self.total)}")
        if self.on_frame:
            self.on_frame(frame_number)

    def _time(self, frame: int) -> str:
        seconds = int(frame / max(1, self.fps))
        return f"{seconds // 60:02d}:{seconds % 60:02d}"

    def _seek_from_scale(self, value: str) -> None:
        if not self.playing and not self.updating_scale:
            self.show_frame(int(float(value)))

    def toggle(self) -> None:
        if not self.capture:
            return
        self.playing = not self.playing
        self.play_button.configure(text="Pause" if self.playing else "Play")
        if self.playing:
            self._tick()

    def _tick(self) -> None:
        if not self.playing or not self.capture:
            return
        current = int(float(self.scale.get())) + 1
        if current >= self.total:
            self.playing = False
            self.play_button.configure(text="Play")
            return
        self.show_frame(current)
        self.after(max(10, int(1000 / max(1, self.fps))), self._tick)


class PlayerTrackingReview(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Orion Player Tracking Studio")
        self.geometry("1280x820")
        self.minsize(1040, 700)
        self.configure(background=PALE)
        self.project = ReviewProject()
        self.crops: dict[str, list[Path]] = {}
        self.cancel_event = threading.Event()
        self.messages: queue.Queue = queue.Queue()
        self._make_style()
        self._make_layout()
        self.after(100, self._poll_messages)

    def _make_style(self) -> None:
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("TFrame", background=PALE)
        style.configure("Card.TFrame", background="white")
        style.configure("TLabel", background=PALE, foreground=NAVY, font=("Arial", 11))
        style.configure("Card.TLabel", background="white", foreground=NAVY, font=("Arial", 11))
        style.configure("Title.TLabel", background=PALE, foreground=NAVY, font=("Arial", 24, "bold"))
        style.configure("Heading.TLabel", background="white", foreground=NAVY, font=("Arial", 15, "bold"))
        style.configure("Accent.TButton", font=("Arial", 11, "bold"), foreground="white", background=ACCENT, padding=8)
        style.map("Accent.TButton", background=[("active", "#255ac0")])
        style.configure("Treeview", rowheight=29, font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

    def _make_layout(self) -> None:
        header = ttk.Frame(self)
        header.pack(fill="x", padx=24, pady=(20, 12))
        title_box = ttk.Frame(header)
        title_box.pack(side="left")
        ttk.Label(title_box, text="Orion Player Tracking Studio", style="Title.TLabel").pack(anchor="w")
        ttk.Label(title_box, text="Track a match, review uncertain results and reconnect player identities.", foreground=MUTED).pack(anchor="w", pady=(3, 0))
        ttk.Button(header, text="Credits", command=self._show_credits, width=8).pack(side="right", anchor="n")

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=24, pady=(0, 12))
        self.start_tab = ttk.Frame(self.tabs, padding=20)
        self.review_tab = ttk.Frame(self.tabs, padding=12)
        self.identity_tab = ttk.Frame(self.tabs, padding=12)
        self.results_tab = ttk.Frame(self.tabs, padding=20)
        self.tabs.add(self.start_tab, text="Start")
        self.tabs.add(self.review_tab, text="Review")
        self.tabs.add(self.identity_tab, text="Players")
        self.tabs.add(self.results_tab, text="Results")
        self._make_start()
        self._make_review()
        self._make_identities()
        self._make_results()

        footer = ttk.Frame(self)
        footer.pack(fill="x", padx=24, pady=(0, 12))
        ttk.Label(footer, text="Sahan Chandimal   Project Orion", foreground=MUTED, font=("Arial", 9)).pack(side="left")
        self.footer_status = ttk.Label(footer, text="Ready", foreground=MUTED, font=("Arial", 9))
        self.footer_status.pack(side="right")

    def _make_start(self) -> None:
        card = ttk.Frame(self.start_tab, style="Card.TFrame", padding=24)
        card.pack(fill="x")
        ttk.Label(card, text="Start with a video", style="Heading.TLabel").grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 14))
        ttk.Label(card, text="Video", style="Card.TLabel").grid(row=1, column=0, sticky="w", pady=8)
        self.video_var = tk.StringVar()
        ttk.Entry(card, textvariable=self.video_var).grid(row=1, column=1, sticky="ew", padx=12)
        ttk.Button(card, text="Choose video", command=self._choose_video).grid(row=1, column=2)
        ttk.Label(card, text="Model", style="Card.TLabel").grid(row=2, column=0, sticky="w", pady=8)
        self.model_var = tk.StringVar()
        ttk.Entry(card, textvariable=self.model_var).grid(row=2, column=1, sticky="ew", padx=12)
        ttk.Button(card, text="Choose model", command=self._choose_model).grid(row=2, column=2)
        ttk.Label(card, text="Tracking CSV", style="Card.TLabel").grid(row=3, column=0, sticky="w", pady=8)
        self.csv_var = tk.StringVar()
        ttk.Entry(card, textvariable=self.csv_var).grid(row=3, column=1, sticky="ew", padx=12)
        ttk.Button(card, text="Choose CSV", command=self._choose_csv).grid(row=3, column=2)
        ttk.Label(card, text="Tracker", style="Card.TLabel").grid(row=4, column=0, sticky="w", pady=8)
        self.tracker_var = tk.StringVar(value="ByteTrack")
        ttk.Combobox(card, textvariable=self.tracker_var, values=["ByteTrack", "BoTSORT"], state="readonly", width=18).grid(row=4, column=1, sticky="w", padx=12)
        ttk.Label(card, text="Frame limit", style="Card.TLabel").grid(row=5, column=0, sticky="w", pady=8)
        self.limit_var = tk.StringVar(value="")
        ttk.Entry(card, textvariable=self.limit_var, width=20).grid(row=5, column=1, sticky="w", padx=12)
        card.columnconfigure(1, weight=1)

        actions = ttk.Frame(self.start_tab)
        actions.pack(fill="x", pady=18)
        ttk.Button(actions, text="Run sample match", command=self._run_sample).pack(side="left")
        ttk.Button(actions, text="Load existing results", command=self._load_existing).pack(side="right", padx=(10, 0))
        ttk.Button(actions, text="Start analysis", style="Accent.TButton", command=self._start_tracking).pack(side="right")
        ttk.Button(actions, text="Stop", command=self._stop_tracking).pack(side="right", padx=(0, 10))

        progress_card = ttk.Frame(self.start_tab, style="Card.TFrame", padding=24)
        progress_card.pack(fill="x")
        self.stage_label = ttk.Label(progress_card, text="Choose a video and model, or load an existing tracking CSV.", style="Card.TLabel")
        self.stage_label.pack(anchor="w")
        self.progress = ttk.Progressbar(progress_card, mode="determinate")
        self.progress.pack(fill="x", pady=(12, 0))
        ttk.Label(progress_card, text="The selected model decides which classes can be detected. All team and jumper results can be reviewed before export.", style="Card.TLabel", foreground=MUTED, wraplength=900).pack(anchor="w", pady=(12, 0))

    def _make_review(self) -> None:
        pane = ttk.Panedwindow(self.review_tab, orient="horizontal")
        pane.pack(fill="both", expand=True)
        left = ttk.Frame(pane)
        right = ttk.Frame(pane, style="Card.TFrame", padding=12)
        pane.add(left, weight=3)
        pane.add(right, weight=2)
        self.video_panel = VideoPanel(left)
        self.video_panel.pack(fill="both", expand=True)
        ttk.Label(right, text="Problem timestamps", style="Heading.TLabel").pack(anchor="w", pady=(0, 8))
        self.event_tree = ttk.Treeview(right, columns=("time", "kind", "status"), show="headings", selectmode="browse")
        for column, text, width in (("time", "Time", 75), ("kind", "Issue", 180), ("status", "Status", 100)):
            self.event_tree.heading(column, text=text)
            self.event_tree.column(column, width=width, anchor="w")
        self.event_tree.pack(fill="both", expand=True)
        self.event_tree.bind("<<TreeviewSelect>>", self._jump_to_event)
        self.event_detail = ttk.Label(right, text="Select an item to review it.", style="Card.TLabel", wraplength=360)
        self.event_detail.pack(fill="x", pady=10)
        event_actions = ttk.Frame(right, style="Card.TFrame")
        event_actions.pack(fill="x")
        ttk.Button(event_actions, text="Correct", command=lambda: self._set_event_status("Correct")).pack(side="left")
        ttk.Button(event_actions, text="False alarm", command=lambda: self._set_event_status("False alarm")).pack(side="left", padx=6)
        ttk.Button(event_actions, text="Needs review", command=lambda: self._set_event_status("Needs review")).pack(side="left")

    def _make_identities(self) -> None:
        pane = ttk.Panedwindow(self.identity_tab, orient="horizontal")
        pane.pack(fill="both", expand=True)
        table_frame = ttk.Frame(pane)
        editor = ttk.Frame(pane, style="Card.TFrame", padding=18)
        pane.add(table_frame, weight=4)
        pane.add(editor, weight=2)
        self.track_tree = ttk.Treeview(table_frame, columns=("track", "class", "team", "jumper", "identity", "frames"), show="headings", selectmode="extended")
        for column, text, width in (
            ("track", "Track", 70), ("class", "Class", 100), ("team", "Team", 120),
            ("jumper", "Jumper", 70), ("identity", "Player identity", 170), ("frames", "Frames", 90),
        ):
            self.track_tree.heading(column, text=text)
            self.track_tree.column(column, width=width, anchor="w")
        self.track_tree.pack(fill="both", expand=True)
        self.track_tree.bind("<<TreeviewSelect>>", self._load_track_editor)

        ttk.Label(editor, text="Review player", style="Heading.TLabel").pack(anchor="w")
        ttk.Label(editor, text="Team", style="Card.TLabel").pack(anchor="w", pady=(18, 3))
        self.team_var = tk.StringVar()
        ttk.Entry(editor, textvariable=self.team_var).pack(fill="x")
        ttk.Label(editor, text="Jumper number", style="Card.TLabel").pack(anchor="w", pady=(12, 3))
        self.jumper_var = tk.StringVar()
        ttk.Entry(editor, textvariable=self.jumper_var).pack(fill="x")
        ttk.Button(editor, text="Save correction", style="Accent.TButton", command=self._save_track).pack(fill="x", pady=(14, 5))
        ttk.Separator(editor).pack(fill="x", pady=15)
        ttk.Button(editor, text="Suggest teams from colours", command=self._analyse_teams).pack(fill="x", pady=4)
        ttk.Button(editor, text="Read jumper numbers", command=self._read_jumpers).pack(fill="x", pady=4)
        ttk.Label(editor, text="Merge selected tracks as", style="Card.TLabel").pack(anchor="w", pady=(18, 3))
        self.merge_var = tk.StringVar()
        ttk.Entry(editor, textvariable=self.merge_var).pack(fill="x")
        ttk.Button(editor, text="Merge selected tracks", command=self._merge_tracks).pack(fill="x", pady=6)

    def _make_results(self) -> None:
        self.summary_label = ttk.Label(self.results_tab, text="Load tracking results to see the summary.", style="Title.TLabel")
        self.summary_label.pack(anchor="w")
        self.metrics_frame = ttk.Frame(self.results_tab)
        self.metrics_frame.pack(fill="x", pady=24)
        self.result_detail = ttk.Label(self.results_tab, text="", wraplength=900)
        self.result_detail.pack(anchor="w")
        ttk.Button(self.results_tab, text="Export results", style="Accent.TButton", command=self._export).pack(anchor="w", pady=22)

    def _choose_video(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.mov *.avi *.mkv"), ("All files", "*")])
        if path:
            self.video_var.set(path)

    def _choose_model(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("Model files", "*.pt *.onnx"), ("All files", "*")])
        if path:
            self.model_var.set(path)
            self._inspect_model(path)

    def _choose_csv(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*")])
        if path:
            self.csv_var.set(path)

    def _inspect_model(self, path: str) -> None:
        def work() -> None:
            try:
                classes = inspect_model(path)
                self.messages.put(("status", f"Model classes: {', '.join(classes)}"))
            except Exception as exc:
                self.messages.put(("error", str(exc)))
        threading.Thread(target=work, daemon=True).start()

    def _start_tracking(self) -> None:
        video = self.video_var.get().strip()
        model = self.model_var.get().strip()
        if not video or not model:
            messagebox.showinfo("Choose files", "Choose a match video and a model first.")
            return
        try:
            limit = int(self.limit_var.get()) if self.limit_var.get().strip() else None
        except ValueError:
            messagebox.showerror("Frame limit", "Enter a whole number or leave the frame limit empty.")
            return
        tracker = "bytetrack.yaml" if self.tracker_var.get() == "ByteTrack" else "botsort.yaml"
        self.progress.configure(value=0)
        self.cancel_event.clear()

        def progress(done: int, total: int, stage: str) -> None:
            self.messages.put(("progress", done, total, stage))

        def work() -> None:
            try:
                out_video, out_csv, fps = track_video(video, model, ROOT / "outputs" / "review_runs", tracker, max_frames=limit, progress=progress, cancel=self.cancel_event)
                self.messages.put(("tracking_done", video, str(out_video), str(out_csv), fps, model))
            except Exception as exc:
                self.messages.put(("error", str(exc)))
        threading.Thread(target=work, daemon=True).start()

    def _stop_tracking(self) -> None:
        self.cancel_event.set()
        self.stage_label.configure(text="Stopping after the current frame")

    def _load_existing(self) -> None:
        video = self.video_var.get().strip()
        csv_path = self.csv_var.get().strip()
        if not video or not csv_path:
            messagebox.showinfo("Choose files", "Choose a video and its tracking CSV first.")
            return
        self._open_project(video, csv_path, self.model_var.get().strip())

    def _run_sample(self) -> None:
        sample_video = ROOT / "outputs" / "sample_match.mp4"
        sample_csv = ROOT / "outputs" / "sample_match.csv"
        if not sample_video.exists():
            messagebox.showinfo("Sample match", "Add sample_match.mp4 to the outputs folder, or choose your own video.")
            return
        self.video_var.set(str(sample_video))
        if sample_csv.exists():
            self.csv_var.set(str(sample_csv))
            self._open_project(str(sample_video), str(sample_csv), "")
        else:
            self.project = ReviewProject(video_path=str(sample_video))
            self.video_panel.load(str(sample_video), [], None)
            self.tabs.select(self.review_tab)
            self.footer_status.configure(text="Sample video loaded without tracking data")

    def _open_project(self, video: str, csv_path: str, model: str = "", fps: float | None = None) -> None:
        try:
            self.project = ReviewProject(video_path=video, model_path=model, fps=fps or 25.0)
            self.project.load_csv(csv_path)
            try:
                import cv2
                capture = cv2.VideoCapture(video)
                actual_fps = capture.get(cv2.CAP_PROP_FPS) or self.project.fps
                capture.release()
                self.project.fps = actual_fps
                self.project.events = find_review_events(self.project.rows, actual_fps)
            except Exception:
                pass
            self.video_panel.load(video, self.project.rows, self.project.fps)
            self._refresh_events()
            self._refresh_tracks()
            self._refresh_results()
            self.tabs.select(self.review_tab)
            self.stage_label.configure(text="Review ready")
            self.progress.configure(value=100)
            self.footer_status.configure(text=f"Loaded {len(self.project.rows):,} detections")
        except Exception as exc:
            messagebox.showerror("Could not load results", str(exc))

    def _refresh_events(self) -> None:
        self.event_tree.delete(*self.event_tree.get_children())
        for index, event in enumerate(self.project.events):
            self.event_tree.insert("", "end", iid=str(index), values=(event.timestamp, event.kind, event.status))

    def _jump_to_event(self, _event=None) -> None:
        selection = self.event_tree.selection()
        if not selection:
            return
        event = self.project.events[int(selection[0])]
        self.event_detail.configure(text=event.detail)
        self.video_panel.playing = False
        self.video_panel.play_button.configure(text="Play")
        self.video_panel.show_frame(event.frame)

    def _set_event_status(self, status: str) -> None:
        selection = self.event_tree.selection()
        if not selection:
            return
        event = self.project.events[int(selection[0])]
        event.status = status
        self.event_tree.set(selection[0], "status", status)
        self._refresh_results()

    def _refresh_tracks(self) -> None:
        self.track_tree.delete(*self.track_tree.get_children())
        for track_id, track in sorted(self.project.tracks.items(), key=lambda item: (int(item[0]) if item[0].isdigit() else 10**9, item[0])):
            self.track_tree.insert("", "end", iid=track_id, values=(track_id, track.class_name, track.team, track.jumper, track.stable_id, track.detections))

    def _load_track_editor(self, _event=None) -> None:
        selection = self.track_tree.selection()
        if not selection:
            return
        track = self.project.tracks[selection[0]]
        self.team_var.set(track.team)
        self.jumper_var.set(track.jumper)

    def _save_track(self) -> None:
        selection = self.track_tree.selection()
        if not selection:
            messagebox.showinfo("Select a track", "Select a track first.")
            return
        for track_id in selection:
            self.project.set_track_value(track_id, "team", self.team_var.get())
            self.project.set_track_value(track_id, "jumper", self.jumper_var.get())
        self._refresh_tracks()
        self._refresh_results()

    def _ensure_crops(self) -> dict[str, list[Path]]:
        if not self.crops:
            self.crops = extract_track_crops(self.project.video_path, self.project.rows, ROOT / "outputs" / "review_crops", progress=lambda text: self.messages.put(("status", text)))
        return self.crops

    def _analyse_teams(self) -> None:
        if not self.project.rows:
            return
        def work() -> None:
            try:
                crops = self._ensure_crops()
                classes = {track_id: track.class_name for track_id, track in self.project.tracks.items()}
                teams = suggest_teams(crops, classes)
                self.messages.put(("teams_done", teams))
            except Exception as exc:
                self.messages.put(("error", str(exc)))
        threading.Thread(target=work, daemon=True).start()

    def _read_jumpers(self) -> None:
        if not self.project.rows:
            return
        def work() -> None:
            try:
                answers = run_ocr(self._ensure_crops(), progress=lambda text: self.messages.put(("status", text)))
                self.messages.put(("ocr_done", answers))
            except Exception as exc:
                self.messages.put(("error", str(exc)))
        threading.Thread(target=work, daemon=True).start()

    def _merge_tracks(self) -> None:
        selection = self.track_tree.selection()
        try:
            self.project.merge_tracks(selection, self.merge_var.get())
        except ValueError as exc:
            messagebox.showinfo("Player identity", str(exc))
            return
        self._refresh_tracks()
        self._refresh_results()

    def _refresh_results(self) -> None:
        for child in self.metrics_frame.winfo_children():
            child.destroy()
        tracks = list(self.project.tracks.values())
        stable = {track.stable_id for track in tracks}
        reviewed_events = sum(event.status != "Needs review" for event in self.project.events)
        values = [
            ("Temporary tracks", len(tracks)),
            ("Player identities", len(stable)),
            ("Problem timestamps", len(self.project.events)),
            ("Reviewed issues", reviewed_events),
        ]
        for index, (label, value) in enumerate(values):
            card = ttk.Frame(self.metrics_frame, style="Card.TFrame", padding=18)
            card.grid(row=0, column=index, sticky="nsew", padx=(0, 10))
            ttk.Label(card, text=f"{value:,}", style="Heading.TLabel").pack(anchor="w")
            ttk.Label(card, text=label, style="Card.TLabel", foreground=MUTED).pack(anchor="w")
            self.metrics_frame.columnconfigure(index, weight=1)
        self.summary_label.configure(text="Tracking review summary")
        output_text = f" The annotated video is saved at {self.project.annotated_video_path}." if self.project.annotated_video_path else ""
        self.result_detail.configure(text="The export keeps the original temporary track IDs, reviewed team and jumper values, resolved player identities and every problem timestamp decision." + output_text)

    def _export(self) -> None:
        if not self.project.rows:
            messagebox.showinfo("Nothing to export", "Load tracking results first.")
            return
        folder = filedialog.askdirectory(title="Choose export folder")
        if folder:
            paths = self.project.export(folder)
            messagebox.showinfo("Export complete", f"Saved reviewed tracks, events and project data in\n{Path(folder)}")
            self.footer_status.configure(text=f"Exported {len(paths)} files")

    def _show_credits(self) -> None:
        window = tk.Toplevel(self)
        window.title("Credits")
        window.geometry("520x420")
        window.configure(background="white")
        frame = ttk.Frame(window, style="Card.TFrame", padding=22)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Project work used in this tool", style="Heading.TLabel").pack(anchor="w", pady=(0, 12))
        text = (
            "Main tool contributor\nSahan Chandimal\n\n"
            "Repository work connected here\n"
            "Christopher Abbey   initial tracking pipeline\n"
            "Sri Bandara   model and tracking scripts\n"
            "Matthew Lewis   team colour tracking and jumper data collection\n"
            "Hasini Siddu   crop extraction and OCR testing\n"
            "Yash Talati   tracking diagnostics and ID stability\n"
            "Lê Đông Quân   jersey colour service"
        )
        ttk.Label(frame, text=text, style="Card.TLabel", justify="left", wraplength=460).pack(anchor="w")
        ttk.Button(frame, text="Close", command=window.destroy).pack(anchor="e", pady=(18, 0))

    def _poll_messages(self) -> None:
        try:
            while True:
                message = self.messages.get_nowait()
                kind = message[0]
                if kind == "status":
                    self.stage_label.configure(text=message[1])
                    self.footer_status.configure(text=message[1])
                elif kind == "progress":
                    _, done, total, stage = message
                    self.progress.configure(value=100 * done / max(1, total))
                    self.stage_label.configure(text=f"{stage}   {done:,} of {total:,} frames")
                elif kind == "tracking_done":
                    _, source_video, annotated_video, csv_path, fps, model = message
                    self.video_var.set(source_video)
                    self.csv_var.set(csv_path)
                    self._open_project(source_video, csv_path, model, fps)
                    self.project.annotated_video_path = annotated_video
                    self._refresh_results()
                elif kind == "teams_done":
                    for track_id, team in message[1].items():
                        self.project.set_track_value(track_id, "team", team)
                    self._refresh_tracks()
                    self._refresh_results()
                    self.footer_status.configure(text="Team suggestions ready for review")
                elif kind == "ocr_done":
                    for track_id, jumper in message[1].items():
                        self.project.set_track_value(track_id, "jumper", jumper)
                    self._refresh_tracks()
                    self._refresh_results()
                    self.footer_status.configure(text="Jumper suggestions ready for review")
                elif kind == "error":
                    messagebox.showerror("Could not complete the action", message[1])
                    self.footer_status.configure(text="Action stopped")
        except queue.Empty:
            pass
        self.after(100, self._poll_messages)


def main() -> None:
    app = PlayerTrackingReview()
    app.mainloop()


if __name__ == "__main__":
    main()
