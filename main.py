
"""Breathline application entry point."""

import tkinter as tk
from tkinter import ttk, colorchooser
import time

from breathing import calculate_pattern
from interface import BreathingDisplay
from config import load_settings, save_settings

THEMES = {
    "Dark": {
        "background": "#252525",
        "foreground": "#FFFFFF",
        "secondary": "#AAAAAA",
        "inactive": "#454545",
        "trough": "#555555",
        "button": "#444444",
    },
    "Light": {
        "background": "#F2F2F2",
        "foreground": "#222222",
        "secondary": "#666666",
        "inactive": "#D5D5D5",
        "trough": "#CCCCCC",
        "button": "#E0E0E0",
    },
}


class BreathlineApp:
    def __init__(self, root):
        self.root = root

        self.settings = load_settings()

        self.duration = self.settings["duration"]
        self.regulation = self.settings["regulation"]
        self.tempo = self.settings["tempo"]
        self.inhale_color = self.settings["inhale_color"]
        self.exhale_color = self.settings["exhale_color"]
        self.theme = self.settings["theme"]

        self.root.title("Breathline")
        self.root.geometry(self.settings["window_geometry"])
        self.root.minsize(400, 125)

        self.elapsed_before_pause = 0.0
        self.session_start = None
        self.running = False
        self.session_complete = False
        self.after_id = None

        self.pattern = calculate_pattern(
            self.regulation,
            self.tempo
        )

        if self.theme not in THEMES:
            self.theme = "Dark"

        self.build_interface()
        self.change_theme(self.theme)

        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self.animation_start = time.monotonic()
        self.animate()

    def build_interface(self):
        self.root.configure(bg="#252525")

        # Scrollable application area
        scroll_area = tk.Frame(self.root, bg="#252525")
        scroll_area.pack(fill="both", expand=True)

        canvas = tk.Canvas(
            scroll_area,
            bg="#252525",
            highlightthickness=0
        )
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            scroll_area,
            orient="vertical",
            command=canvas.yview
        )
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)

        container = tk.Frame(
            canvas,
            bg="#252525",
            padx=20,
            pady=3
        )

        container_window = canvas.create_window(
            (0, 0),
            window=container,
            anchor="nw"
        )

        def update_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def update_container_width(event):
            canvas.itemconfigure(
                container_window,
                width=event.width
            )

        container.bind("<Configure>", update_scroll_region)
        canvas.bind("<Configure>", update_container_width)

        # Windows mouse-wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(
                int(-event.delta / 120),
                "units"
            )

        canvas.bind("<Enter>", lambda event: canvas.bind_all(
            "<MouseWheel>", on_mousewheel
        ))
        canvas.bind("<Leave>", lambda event: canvas.unbind_all(
            "<MouseWheel>"
        ))

        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        view_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="View", menu=view_menu)

        settings_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)

        settings_menu.add_command(
            label="Inhale color...",
            command=self.choose_inhale_color
        )

        settings_menu.add_command(
            label="Exhale color...",
            command=self.choose_exhale_color
        )

        theme_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Theme", menu=theme_menu)

        self.theme_var = tk.StringVar(value=self.theme)

        theme_menu.add_radiobutton(
            label="Dark",
            variable=self.theme_var,
            value="Dark",
            command=lambda: self.change_theme("Dark")
        )

        theme_menu.add_radiobutton(
            label="Light",
            variable=self.theme_var,
            value="Light",
            command=lambda: self.change_theme("Light")
        )

        self.display = BreathingDisplay(
            container,
            height=120,
            bg="#252525",
            inhale_color=self.inhale_color,
            exhale_color=self.exhale_color
        )
        self.display.pack(fill="x", expand=False, pady=(0, 10))
        self.display.pack_propagate(False)

        initial_time = (
            f"{self.duration // 60:02d}:"
            f"{self.duration % 60:02d}"
        )
        self.countdown_label = tk.Label(
            container,
            text=initial_time,
            font=("Segoe UI", 28, "bold"),
            fg="white",
            bg="#252525"
        )
        self.countdown_label.pack(pady=10)

        # Regulation control
        tk.Label(
            container,
            text="REGULATION",
            font=("Segoe UI", 10, "bold"),
            fg="white",
            bg="#252525"
        ).pack(pady=(10, 0))

        tk.Label(
            container,
            text="Calming ← → Energizing",
            font=("Segoe UI", 9),
            fg="#AAAAAA",
            bg="#252525"
        ).pack()

        regulation_row = tk.Frame(container, bg="#252525")
        regulation_row.pack(fill="x")

        ttk.Button(
            regulation_row,
            text="−",
            width=3,
            command=lambda: self.adjust_regulation(-0.1)
        ).pack(side="left")

        self.regulation_scale = tk.Scale(
            regulation_row,
            from_=-1,
            to=1,
            resolution=0.1,
            orient="horizontal",
            showvalue=True,
            command=self.set_regulation,
            bg="#252525",
            fg="white",
            troughcolor="#555555",
            highlightthickness=0,
            length=300
        )
        self.regulation_scale.set(self.regulation)
        self.regulation_scale.pack(side="left", fill="x", expand=True)

        ttk.Button(
            regulation_row,
            text="+",
            width=3,
            command=lambda: self.adjust_regulation(0.1)
        ).pack(side="left")

        # Rhythm control
        tk.Label(
            container,
            text="TEMPO",
            font=("Segoe UI", 10, "bold"),
            fg="white",
            bg="#252525"
        ).pack(pady=(10, 0))

        tk.Label(
            container,
            text="Slower ← → Faster",
            font=("Segoe UI", 9),
            fg="#AAAAAA",
            bg="#252525"
        ).pack()

        tempo_row = tk.Frame(container, bg="#252525")
        tempo_row.pack(fill="x")

        ttk.Button(
            tempo_row,
            text="−",
            width=3,
            command=lambda: self.adjust_tempo(-0.1)
        ).pack(side="left")

        self.tempo_scale = tk.Scale(
            tempo_row,
            from_=-1,
            to=1,
            resolution=0.1,
            orient="horizontal",
            showvalue=True,
            command=self.set_tempo,
            bg="#252525",
            fg="white",
            troughcolor="#555555",
            highlightthickness=0,
            length=300
        )
        self.tempo_scale.set(self.tempo)
        self.tempo_scale.pack(side="left", fill="x", expand=True)

        ttk.Button(
            tempo_row,
            text="+",
            width=3,
            command=lambda: self.adjust_tempo(0.1)
        ).pack(side="left")

        # Session duration control
        duration_row = tk.Frame(container, bg="#252525")
        duration_row.pack(pady=10)

        tk.Label(
            duration_row,
            text="SESSION LENGTH (MINUTES)",
            font=("Segoe UI", 10, "bold"),
            fg="white",
            bg="#252525"
        ).pack()

        self.duration_var = tk.IntVar(value=self.duration // 60)

        self.duration_selector = tk.Spinbox(
            duration_row,
            from_=5,
            to=180,
            increment=5,
            textvariable=self.duration_var,
            width=6,
            command=self.set_duration
        )
        self.duration_selector.pack(pady=5)

        self.duration_selector.bind(
            "<FocusOut>",
            lambda event: self.set_duration()
        )

        self.duration_selector.bind(
            "<Return>",
            lambda event: self.set_duration()
        )

        self.timer_status_label = tk.Label(
            container,
            text="Ready",
            font=("Segoe UI", 12, "bold"),
            fg="#AAAAAA",
            bg="#252525"
        )
        self.timer_status_label.pack(pady=5)

        controls = tk.Frame(container, bg="#252525")
        controls.pack(pady=15)

        ttk.Button(
            controls, text="Start", command=self.start
        ).pack(side="left", padx=5)

        ttk.Button(
            controls, text="Pause", command=self.pause
        ).pack(side="left", padx=5)

        ttk.Button(
            controls, text="Reset", command=self.reset
        ).pack(side="left", padx=5)

    def choose_inhale_color(self):
        result = colorchooser.askcolor(
            color=self.inhale_color,
            title="Choose inhale color",
            parent=self.root
        )

        if result[1]:
            self.inhale_color = result[1]
            self.display.set_colors(
                self.inhale_color,
                self.exhale_color
            )

    def choose_exhale_color(self):
        result = colorchooser.askcolor(
            color=self.exhale_color,
            title="Choose exhale color",
            parent=self.root
        )

        if result[1]:
            self.exhale_color = result[1]
            self.display.set_colors(
                self.inhale_color,
                self.exhale_color
            )

    def change_theme(self, theme):
        self.theme = theme
        colors = THEMES[theme]

        self.root.configure(bg=colors["background"])

        def update_widgets(parent):
            for widget in parent.winfo_children():
                if isinstance(widget, (tk.Frame, tk.Label)):
                    widget.configure(
                        bg=colors["background"]
                    )

                    if isinstance(widget, tk.Label):
                        text = widget.cget("text")

                        if text in (
                            "Calming ← → Energizing",
                            "Slower ← → Faster",
                            "Ready",
                            "Paused",
                        ):
                            widget.configure(
                                fg=colors["secondary"]
                            )
                        elif text == "SESSION COMPLETE":
                            widget.configure(fg="#FF5555")
                        else:
                            widget.configure(
                                fg=colors["foreground"]
                            )

                elif isinstance(widget, tk.Scale):
                    widget.configure(
                        bg=colors["background"],
                        fg=colors["foreground"],
                        troughcolor=colors["trough"],
                        highlightbackground=colors["background"],
                        activebackground=colors["button"]
                    )

                update_widgets(widget)

        update_widgets(self.root)

        self.display.set_theme_colors(
            colors["background"],
            colors["inactive"]
        )

    def update_pattern(self):
        self.pattern = calculate_pattern(
            self.regulation,
            self.tempo
        )

    def set_regulation(self, value):
        self.regulation = float(value)
        self.update_pattern()

    def set_tempo(self, value):
        self.tempo = float(value)
        self.update_pattern()

    def adjust_regulation(self, amount):
        value = round(
            max(-1.0, min(1.0, self.regulation + amount)), 1
        )
        self.regulation_scale.set(value)
        self.set_regulation(value)

    def adjust_tempo(self, amount):
        value = round(
            max(-1.0, min(1.0, self.tempo + amount)), 1
        )
        self.tempo_scale.set(value)
        self.set_tempo(value)

    def set_duration(self):
        try:
            minutes = max(5, min(180, int(self.duration_var.get())))
            minutes = round(minutes / 5) * 5

            self.duration_var.set(minutes)
            self.duration = minutes * 60

            if not self.running:
                self.reset()

        except (ValueError, tk.TclError):
            self.duration_var.set(self.duration // 60)

    def start(self):
        if self.running:
            return
        if self.session_complete:
            self.reset()

        self.running = True
        self.session_start = time.monotonic()
        self.update_timer()

    def pause(self):
        if not self.running:
            return

        self.elapsed_before_pause += (
            time.monotonic() - self.session_start
        )

        self.running = False

        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.timer_status_label.config(
            text="Paused",
            fg="#AAAAAA"
        )

    def reset(self):
        was_complete = self.session_complete
        self.pause()
        self.elapsed_before_pause = 0.0
        self.session_start = None
        self.session_complete = False
        self.change_theme(self.theme)
        if was_complete:
            self.animation_start = time.monotonic()
            self.animate()

        self.timer_status_label.config(
            text="Ready",
            fg="#AAAAAA"
        )

        self.countdown_label.config(
            text=f"{self.duration // 60:02d}:{self.duration % 60:02d}"
        )

    def update_timer(self):
        if not self.running:
            return

        elapsed = (
            self.elapsed_before_pause
            + time.monotonic() - self.session_start
        )

        remaining = max(0, self.duration - elapsed)

        minutes = int(remaining) // 60
        seconds = int(remaining) % 60

        self.countdown_label.config(
            text=f"{minutes:02d}:{seconds:02d}"
        )

        if remaining <= 0:
            self.running = False
            self.session_complete = True

            self.timer_status_label.config(
                text="SESSION COMPLETE",
                fg="#FF5555"
            )

            if self.animation_id:
                self.root.after_cancel(self.animation_id)
                self.animation_id = None

            self.display.set_completion_state()
            return

        self.after_id = self.root.after(250, self.update_timer)

    def animate(self):
        if self.session_complete:
            return
        elapsed = time.monotonic() - self.animation_start

        cycle = self.pattern.cycle_duration
        position = elapsed % cycle

        if position < self.pattern.inhale:
            phase = "inhale"
            progress = position / self.pattern.inhale
        else:
            phase = "exhale"
            progress = (
                position - self.pattern.inhale
            ) / self.pattern.exhale

        progress = 1 - (1 - progress) ** 2.7

        self.display.set_progress(phase, progress)

        self.animation_id = self.root.after(40, self.animate)

    def close(self):
        self.settings.update({
            "duration": self.duration,
            "regulation": self.regulation,
            "tempo": self.tempo,
            "inhale_color": self.inhale_color,
            "exhale_color": self.exhale_color,
            "theme": self.theme,
            "window_geometry": self.root.geometry()
        })

        save_settings(self.settings)

        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = BreathlineApp(root)
    root.mainloop()

