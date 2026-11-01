
"""Breathline visual breathing display."""

import tkinter as tk


class BreathingDisplay(tk.Frame):
    def __init__(
        self,
        parent,
        inhale_color="#55B8E8",
        exhale_color="#E6A15C",
        background_color="#252525",
        inactive_color="#454545",
        rows=24,
        **kwargs
    ):
        super().__init__(parent, **kwargs)

        self.rows = rows
        self.inhale_color = inhale_color
        self.exhale_color = exhale_color
        self.background_color = background_color
        self.inactive_color = inactive_color
        self.progress = 0.0
        self.phase = "inhale"

        self.canvas = tk.Canvas(
            self,
            background=self.background_color,
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<Configure>", self.draw)

    def set_progress(self, phase, progress):
        self.phase = phase
        self.progress = max(0.0, min(1.0, progress))
        self.draw()

    def set_colors(self, inhale_color, exhale_color):
        self.inhale_color = inhale_color
        self.exhale_color = exhale_color
        self.draw()

    def set_theme_colors(self, background_color, inactive_color):
        self.background_color = background_color
        self.inactive_color = inactive_color
        self.canvas.configure(background=background_color)
        self.draw()

    def set_completion_state(self):
        completion_color = "#713B3B"
        self.background_color = completion_color
        self.inactive_color = completion_color
        self.canvas.configure(background=completion_color)
        self.draw()

    def draw(self, event=None):
        self.canvas.delete("all")

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width < 2 or height < 2:
            return

        gap = 1 
        row_height = (height - gap * (self.rows - 1)) / self.rows

        if self.phase == "inhale":
            active_rows = round(self.progress * self.rows)
            color = self.inhale_color
        else:
            active_rows = round((1 - self.progress) * self.rows)
            color = self.exhale_color

        for i in range(self.rows):
            y1 = i * (row_height + gap)
            y2 = y1 + row_height

            is_active = i >= self.rows - active_rows

            self.canvas.create_rectangle(
                0, y1, width, y2,
                fill=color if is_active else self.inactive_color,
                outline=""
            )

