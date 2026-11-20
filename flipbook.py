from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageDraw, ImageTk

from frames import FRAME_COUNT, FRAME_DELAY_MS, SIZE, export_gif, new_frames, render_frame


ZOOM = 16
DISPLAY_SIZE = SIZE * ZOOM


class FlipbookEditor:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.frames = new_frames()
        self.selected_frame = tk.IntVar(root, value=0)
        self.tool = tk.StringVar(root, value="Pencil")
        self.last_pixel: tuple[int, int] | None = None
        self.playback_job: str | None = None

        root.title("Onion Skin Flipbook")
        root.resizable(False, False)
        root.protocol("WM_DELETE_WINDOW", self.close)

        panel = ttk.Frame(root, padding=16)
        panel.pack()
        toolbar = ttk.Frame(panel)
        toolbar.pack(fill=tk.X, pady=(0, 12))
        self.tools = []
        for name in ("Pencil", "Eraser"):
            button = ttk.Radiobutton(
                toolbar, text=name, value=name, variable=self.tool, style="Toolbutton"
            )
            button.pack(side=tk.LEFT, padx=(0, 4))
            self.tools.append(button)
        self.play_button = ttk.Button(toolbar, text="Play", command=self.toggle_playback)
        self.play_button.pack(side=tk.LEFT, padx=(12, 0))
        ttk.Button(toolbar, text="Export GIF…", command=self.export).pack(side=tk.RIGHT)

        border = ttk.Frame(panel, borderwidth=1, relief=tk.SOLID)
        border.pack()
        self.canvas = tk.Canvas(
            border, width=DISPLAY_SIZE, height=DISPLAY_SIZE,
            highlightthickness=0, borderwidth=0, cursor="crosshair",
        )
        self.canvas.pack()
        self.canvas_image = self.canvas.create_image(0, 0, anchor=tk.NW)
        self.canvas.bind("<Button-1>", self.begin_stroke)
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.end_stroke)

        frame_strip = ttk.Frame(panel)
        frame_strip.pack(fill=tk.X, pady=(12, 0))
        for index in range(FRAME_COUNT):
            frame_strip.columnconfigure(index, weight=1, uniform="frame")
            ttk.Radiobutton(
                frame_strip, text=str(index + 1), value=index, variable=self.selected_frame,
                command=self.show_editor, style="Toolbutton",
            ).grid(row=0, column=index, sticky="ew", padx=2)

        self.show_editor()

    def show_frame(self, index: int, *, editing: bool) -> None:
        guide = self.frames[index - 1] if editing and index > 0 else None
        image = render_frame(self.frames[index], guide)
        enlarged = image.resize((DISPLAY_SIZE, DISPLAY_SIZE), Image.Resampling.NEAREST)
        self.photo = ImageTk.PhotoImage(enlarged, master=self.root)
        self.canvas.itemconfigure(self.canvas_image, image=self.photo)

    def show_editor(self) -> None:
        if self.playback_job is not None:
            self.root.after_cancel(self.playback_job)
            self.playback_job = None
            self.play_button.configure(text="Play")
            self.canvas.configure(cursor="crosshair")
            for button in self.tools:
                button.state(["!disabled"])
        self.last_pixel = None
        self.show_frame(self.selected_frame.get(), editing=True)

    def begin_stroke(self, event: tk.Event) -> None:
        self.last_pixel = None
        self.paint(event)

    def paint(self, event: tk.Event) -> None:
        if self.playback_job is not None:
            return
        x, y = event.x // ZOOM, event.y // ZOOM
        if not (0 <= x < SIZE and 0 <= y < SIZE):
            self.last_pixel = None
            return
        pixel = (x, y)
        index = self.selected_frame.get()
        fill = 255 if self.tool.get() == "Pencil" else 0
        ImageDraw.Draw(self.frames[index]).line((self.last_pixel or pixel, pixel), fill=fill)
        self.last_pixel = pixel
        self.show_frame(index, editing=True)

    def end_stroke(self, _event: tk.Event) -> None:
        self.last_pixel = None

    def toggle_playback(self) -> None:
        if self.playback_job is not None:
            self.show_editor()
            return
        self.last_pixel = None
        self.play_button.configure(text="Stop")
        self.canvas.configure(cursor="arrow")
        for button in self.tools:
            button.state(["disabled"])
        self.preview_frame(0)

    def preview_frame(self, index: int) -> None:
        self.show_frame(index, editing=False)
        self.playback_job = self.root.after(
            FRAME_DELAY_MS, self.preview_frame, (index + 1) % FRAME_COUNT
        )

    def export(self) -> None:
        self.show_editor()
        destination = filedialog.asksaveasfilename(
            parent=self.root, title="Export GIF", defaultextension=".gif",
            filetypes=[("GIF images", "*.gif")],
        )
        if destination:
            try:
                export_gif(self.frames, destination)
            except OSError as error:
                messagebox.showerror("Could not export GIF", str(error), parent=self.root)

    def close(self) -> None:
        if self.playback_job is not None:
            self.root.after_cancel(self.playback_job)
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    FlipbookEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
