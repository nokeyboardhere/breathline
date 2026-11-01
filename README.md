
# Breathline

A lightweight desktop breathing app built with Python and Tkinter.

## Features

- Adjustable breathing regulation and tempo.
- Animated breathing display with customizable inhale and exhale colors.
- Light and dark themes.
- Adjustable session timer with start, pause, and reset controls.
- Settings persisted between sessions.
- Resizable, scrollable interface.
- Windows desktop shortcut installer.

## Requirements

- Windows
- Python 3
- Tkinter (usually included with standard Python installations)

No third-party Python packages are required.

## Run from source

Open PowerShell in the project directory:

```powershell
python main.py
```

## Windows desktop shortcut

Run the setup script from PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

This creates a Breathline shortcut on your desktop and uses `icon.png` to generate the Windows icon.

The shortcut launches the app from the project directory, so keep the project folder in its original location.

## Settings

Settings are stored in:

```text
~/.breathline.json
```

They include breathing preferences, colors, session duration, theme, and window geometry.

## Project structure

```text
breathline/
├── main.py
├── breathing.py
├── interface.py
├── config.py
├── setup.ps1
├── icon.png
├── icon.ico
└── README.md
```

## Safety

Breathing patterns are configurable, but individual responses vary. Breathe comfortably and naturally. Stop if you feel dizzy or uncomfortable.

