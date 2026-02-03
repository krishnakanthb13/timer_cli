# Timer CLI

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

![Timer CLI Release v0.0.2](assets/release_v0.0.2_pro.png)

A production-grade, terminal-based Time Management tool for multiple concurrent Timers and Stopwatches.

## Features
-   **Concurrent Timers**: Track multiple projects or tasks simultaneously.
-   **Selection Mode**: Seamlessly navigate and control items using arrow keys.
-   **Custom Naming**: Name your timers (up to 15 chars) for better organization.
-   **Laps Support**: Record multiple laps for stopwatches with live TUI display.
-   **Cross-Platform**: Tailored support for Windows, Linux, and macOS.
-   **Centralized Logging**: All actions are logged to a unified file in `~/.timer_cli/timer_cli.log`.
-   **Sound Notifications**: Automatic system alerts when a timer finishes.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/krishnakanthb13/timer_cli.git
    cd timer_cli
    ```

2.  Install the package:
    ```bash
    pip install .
    ```

## Usage

Launch the dashboard:
```bash
timer-cli
```
*Or use the provided launchers: `run_timer.bat` (Windows) or `run_timer.sh` (Linux/Mac).*

### Controls
| Key | Action |
| :--- | :--- |
| **`[^/v]` Arrows** | Navigate through the list of active items (Selection Mode) |
| **`[</>]` Arrows** | Navigate the action menu (New Timer, etc.) |
| **`Enter`** | **Focus on Item**: Toggle Pause/Resume \| **Focus on Menu**: Execute Action |
| **`[s]`** | Record a **Split/Lap** for the selected stopwatch |
| **`[r]`** | **Reset** the selected timer or stopwatch |
| **`[d]`** | **Delete/Remove** the selected item from the list |
| **`[h]`** | Open the **History** menu (supports **TAB** to toggle Grouped/Raw views) |
| **`[q]`** | Quit the application |

### Timer Input Formats
-   `HH MM SS` (e.g., `1 30 10` for 1 hour, 30 minutes, 10 seconds)
-   `HH MM` (e.g., `1 30` for 1 hour 30 minutes)
-   `MM` (e.g., `10` for 10 minutes)

## Centralized Logging
Timer CLI uses a unified logging system. No matter where you launch the application from, logs will be appended to:
- **Windows**: `%USERPROFILE%\.timer_cli\timer_cli.log`
- **Linux/macOS**: `~/.timer_cli/timer_cli.log`

This ensures a consistent history across all sessions and directories.

## Documentation
For more technical details, refer to:
-   [Code Documentation](CODE_DOCUMENTATION.md)
-   [Design Philosophy](DESIGN_PHILOSOPHY.md)
-   [Contributing Guidelines](CONTRIBUTING.md)

## License
Licensed under the [GPL v3 License](LICENSE).
Copyright (C) 2026 Krishna Kanth B.
