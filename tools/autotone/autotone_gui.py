#!/usr/bin/env python3
"""autotone GUI — a windowed front-end for per-image Lightroom corrections.

Pick a folder of JPEGs, review the proposed correction for every photo,
then apply with one click. Corrections are embedded as Camera Raw develop
settings (see autotone.py); image pixels are never recompressed.
"""

from __future__ import annotations

import os
import queue
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from autotone import analyze, collect_jpegs, describe, embed_xmp, load_for_analysis

DONE_MESSAGE = (
    "Corrections were embedded in {n} photo(s).\n\n"
    "In Lightroom: import the photos and they arrive corrected. For photos "
    "already in your catalog, select them and run Metadata > Read Metadata "
    "from File.\n\nUntouched copies were kept as <name>.jpg.orig."
)


class AutotoneApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("autotone — auto-corrections for Lightroom")
        root.geometry("860x560")
        root.minsize(640, 400)

        self.folder = tk.StringVar()
        self.recursive = tk.BooleanVar(value=False)
        self.backup = tk.BooleanVar(value=True)
        self.strength = tk.DoubleVar(value=1.0)
        self.results: dict[str, object] = {}  # path -> Settings
        self.busy = False
        # Workers never touch tkinter: they push events here and the main
        # thread drains the queue via _poll_events.
        self.events: queue.Queue = queue.Queue()

        pad = {"padx": 8, "pady": 4}

        top = ttk.Frame(root)
        top.pack(fill="x", **pad)
        ttk.Label(top, text="Photo folder:").pack(side="left")
        self.folder_entry = ttk.Entry(top, textvariable=self.folder)
        self.folder_entry.pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(top, text="Browse…", command=self.pick_folder).pack(side="left")

        opts = ttk.Frame(root)
        opts.pack(fill="x", **pad)
        ttk.Checkbutton(opts, text="Include subfolders",
                        variable=self.recursive).pack(side="left")
        ttk.Checkbutton(opts, text="Keep backup copies (.orig)",
                        variable=self.backup).pack(side="left", padx=12)
        ttk.Label(opts, text="Strength:").pack(side="left", padx=(12, 4))
        self.strength_label = ttk.Label(opts, text="1.0", width=4)
        scale = ttk.Scale(opts, from_=0.3, to=1.5, variable=self.strength,
                          length=140, command=self._on_strength)
        scale.pack(side="left")
        self.strength_label.pack(side="left")

        actions = ttk.Frame(root)
        actions.pack(fill="x", **pad)
        self.analyze_btn = ttk.Button(actions, text="Analyze photos",
                                      command=self.start_analyze)
        self.analyze_btn.pack(side="left")
        self.apply_btn = ttk.Button(actions, text="Apply corrections",
                                    command=self.start_apply, state="disabled")
        self.apply_btn.pack(side="left", padx=8)
        self.progress = ttk.Progressbar(actions, mode="determinate", length=220)
        self.progress.pack(side="right")

        table_frame = ttk.Frame(root)
        table_frame.pack(fill="both", expand=True, **pad)
        columns = ("photo", "correction", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.heading("photo", text="Photo")
        self.tree.heading("correction", text="Proposed correction")
        self.tree.heading("status", text="Status")
        self.tree.column("photo", width=240, anchor="w")
        self.tree.column("correction", width=440, anchor="w")
        self.tree.column("status", width=110, anchor="center")
        scroll = ttk.Scrollbar(table_frame, orient="vertical",
                               command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.status = ttk.Label(root, text="Choose a folder of JPEGs, then "
                                           "click Analyze photos.", anchor="w")
        self.status.pack(fill="x", padx=8, pady=(0, 6))

        # A folder dragged onto autotone.exe arrives as a launch argument.
        if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
            self.folder.set(sys.argv[1])
            root.after(200, self.start_analyze)

    # ------------------------------------------------------------------ UI

    def _on_strength(self, _value: str) -> None:
        self.strength_label.config(text=f"{self.strength.get():.1f}")

    def pick_folder(self) -> None:
        chosen = filedialog.askdirectory(title="Choose the folder of JPEGs")
        if chosen:
            self.folder.set(chosen)

    def set_busy(self, busy: bool) -> None:
        self.busy = busy
        state = "disabled" if busy else "normal"
        self.analyze_btn.config(state=state)
        self.apply_btn.config(
            state="disabled" if busy or not self.results else "normal")

    def _update_row(self, path: str, correction: str | None,
                    status: str) -> None:
        name = os.path.basename(path)
        if path in self.tree.get_children(""):
            values = list(self.tree.item(path, "values"))
            if correction is not None:
                values[1] = correction
            values[2] = status
            self.tree.item(path, values=values)
        else:
            self.tree.insert("", "end", iid=path,
                             values=(name, correction or "", status))

    # ------------------------------------------------------------- analyze

    def start_analyze(self) -> None:
        if self.busy:
            return
        folder = self.folder.get().strip().strip('"')
        if not folder or not os.path.isdir(folder):
            messagebox.showwarning("autotone", "Choose a folder first.")
            return
        files = collect_jpegs([folder], self.recursive.get())
        if not files:
            messagebox.showinfo("autotone", "No JPEG files found in that folder.")
            return

        self.results.clear()
        self.tree.delete(*self.tree.get_children(""))
        self.progress.config(maximum=len(files), value=0)
        self.set_busy(True)
        self.status.config(text=f"Analyzing {len(files)} photo(s)…")
        threading.Thread(target=self._analyze_worker,
                         args=(files, self.strength.get()),
                         daemon=True).start()
        self._poll_events()

    def _poll_events(self) -> None:
        while True:
            try:
                event, args = self.events.get_nowait()
            except queue.Empty:
                break
            getattr(self, event)(*args)
        if self.busy:
            self.root.after(50, self._poll_events)

    def _analyze_worker(self, files: list[str], strength: float) -> None:
        done = 0
        for path in files:
            try:
                settings = analyze(load_for_analysis(path), strength)
                text, status = describe(settings), "ready"
            except Exception as exc:
                settings, text, status = None, f"error: {exc}", "failed"
            done += 1
            self.events.put(("_analyze_step",
                             (path, settings, text, status, done, len(files))))
        self.events.put(("_analyze_done", ()))

    def _analyze_step(self, path, settings, text, status, done, total) -> None:
        if settings is not None:
            self.results[path] = settings
        self._update_row(path, text, status)
        self.progress.config(value=done)
        self.status.config(text=f"Analyzing… {done}/{total}")

    def _analyze_done(self) -> None:
        self.set_busy(False)
        n = len(self.results)
        self.status.config(
            text=f"Analysis complete: {n} photo(s) ready. Review the list, "
                 "then click Apply corrections." if n else "Analysis failed "
                 "for every photo — see the list for details.")

    # --------------------------------------------------------------- apply

    def start_apply(self) -> None:
        if self.busy or not self.results:
            return
        n = len(self.results)
        note = ("Untouched .orig copies will be kept."
                if self.backup.get() else
                "No backup copies will be kept (only metadata changes; "
                "pixels are untouched).")
        if not messagebox.askyesno(
                "Apply corrections",
                f"Embed corrections into {n} photo(s)?\n\n{note}"):
            return
        self.progress.config(maximum=n, value=0)
        self.set_busy(True)
        self.status.config(text="Applying corrections…")
        threading.Thread(target=self._apply_worker,
                         args=(dict(self.results), self.backup.get()),
                         daemon=True).start()
        self._poll_events()

    def _apply_worker(self, results: dict, backup: bool) -> None:
        done = 0
        applied = 0
        for path, settings in results.items():
            try:
                embed_xmp(path, settings, backup=backup)
                status = "applied ✓"
                applied += 1
            except Exception as exc:
                status = f"error: {exc}"
            done += 1
            self.events.put(("_apply_step", (path, status, done, len(results))))
        self.events.put(("_apply_done", (applied, len(results))))

    def _apply_step(self, path, status, done, total) -> None:
        self._update_row(path, None, status)
        self.progress.config(value=done)
        self.status.config(text=f"Applying… {done}/{total}")

    def _apply_done(self, applied: int, total: int) -> None:
        self.results.clear()
        self.set_busy(False)
        self.status.config(text=f"Done: {applied}/{total} photo(s) corrected.")
        if applied:
            message = DONE_MESSAGE.format(n=applied)
            if not self.backup.get():
                message = message.rsplit("\n\n", 1)[0]
            messagebox.showinfo("autotone", message)
        if applied < total:
            messagebox.showwarning(
                "autotone", f"{total - applied} photo(s) failed — see the "
                            "Status column.")


def main() -> None:
    root = tk.Tk()
    try:
        ttk.Style().theme_use("vista" if sys.platform == "win32" else "clam")
    except tk.TclError:
        pass
    AutotoneApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
