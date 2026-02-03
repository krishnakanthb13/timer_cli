# Design Philosophy - Timer CLI

## Problem Definition
Most terminal timers are either too simple (single timer, no UI) or too complex (full desktop apps). Users often need to track multiple overlapping events (e.g., cooking multiple items, Pomodoro cycles, or project time tracking) without leaving their primary development environment (the terminal).

## Why This Solution?
Timer CLI provides a **"Headless-First"** yet visually rich experience. It leverages the efficiency of `curses` to provide a dashboard experience that is:
1.  **Non-Blocking**: You can run 10 timers and a stopwatch simultaneously without lag.
2.  **Keyboard-Centric**: Selection Mode allows full control without a mouse.
3.  **Cross-Platform**: A single codebase written in Python that behaves identically on Windows, Linux, and Mac.

## Design Principles
-   **Precision over Polarity**: Time tracking is calculated based on system timestamps (`time.time()`), not loop ticks. This ensures that even if the TUI lags or the window is resized, the time remains accurate.
-   **Modal Transparency**: Input prompts (like naming a timer) are modal but keep the background UI visible, ensuring the user doesn't lose context.
-   **No Hidden State**: All actions (pausing, laps, completion) are documented in a human-readable log file.
-   **Visual Hierarchy**: High-contrast blue headers/footers and progress bars guide the user's eye to high-priority information (remaining time).

## Target Audience
-   Software Engineers and Sysadmins.
-   Productivity enthusiasts who use Tiling Window Managers (i3, Sway, tmux).
-   Anyone who prefers a minimalist, high-performance toolkit.

## Trade-offs & Constraints
-   **Terminal Buffering**: Because it uses `curses`, some extremely old terminal emulators might experience color inconsistencies.
-   **Sound**: relying on system bells or binaries (`afplay`, `winsound`) means sound notifications are dependent on OS configuration (volume, system alerts enabled).
