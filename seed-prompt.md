Timer CLI

- Handle multiple Timers.
- Handles multiple Stop Watches + multiple Laps, until closed.
- View all running Timers / Stop Watches.
- Logging system in place.
- Pause and Resume enabled.
- supports formats for timers -  (hh mm ss, hh mm, mm)
- has a progress bar integrated.
- a fully rotational + navigational menu option loop.
- everything should be handled using keyboard keys

---

### ROLE

You are a **senior systems engineer and CLI UX designer** with deep experience in **Python-based terminal applications**, **state management**, and **interactive TUI/CLI navigation**.

---

### TASK

Design and implement a **production-grade Timer & Stopwatch CLI application** with a **fully navigable, loop-driven menu system**, capable of handling **multiple concurrent timers and stopwatches**, with robust logging and smooth user interaction.

You are responsible for **architecture, data structures, control flow, and UX behavior**.
Do **not** oversimplify—assume this is a serious developer tool.

---

### CORE REQUIREMENTS

#### 1. Timer System

* Support **multiple concurrent timers**
* Accept flexible input formats:
  * `hh mm ss`
  * `hh mm`
  * `mm`
* Each timer must support:
  * Start
  * Pause
  * Resume
  * Cancel
* Display **remaining time + live progress bar**
* Timers continue running until completion or manual stop

---

#### 2. Stopwatch System

* Support **multiple simultaneous stopwatches**
* Each stopwatch must allow:
  * Start
  * Pause
  * Resume
  * Reset
* Support **multiple laps per stopwatch**
* Laps persist **until the application is closed**

---

#### 3. Unified Runtime View

* Provide a **single screen / command** to:
  * View all active timers
  * View all active stopwatches
  * Show their states (running / paused / completed)
* Progress bars must update live without blocking input

---

#### 4. Navigation & Menu System

* Implement a **fully rotational menu loop**:
  * Never exits unless explicitly chosen
* Menu must support:
  * Keyboard-driven navigation
  * Clear action labels
  * Logical hierarchy (Timers / Stopwatches / Logs / Exit)
* Users should always be able to:
  * Go back
  * Switch sections
  * Resume monitoring without restarting processes

---

#### 5. Progress Bar

* Display a **terminal-native progress bar**:
  * Time-based
  * Smooth refresh
  * Non-flickering
* Must work correctly with **multiple simultaneous tasks**

---

#### 6. Logging System

* Implement structured logging:
  * Timer start / pause / resume / completion
  * Stopwatch start / pause / lap / reset
* Each log entry must include:
  * Timestamp
  * Type (Timer / Stopwatch)
  * Action
  * Identifier
* Logs should be:
  * Persisted to a file
  * Viewable from the CLI

---

### TECHNICAL CONSTRAINTS

* Language: **Python**
* Must be **non-blocking** (threading / async / event loop)
* Clean separation of concerns:
  * Core logic
  * UI / menu
  * Logging
  * State management
* Graceful shutdown handling (Ctrl+C safe)

---

### OUTPUT EXPECTATIONS

Produce:

1. **High-level architecture overview**
2. **Data structures & state model**
3. **Menu flow design**
4. **Concurrency strategy**
5. **Complete implementation (or modular files if large)**
6. **Inline explanations only where non-obvious**

Assume this tool will be extended later—design for **clarity, extensibility, and maintainability**.

---

### QUALITY BAR

* No toy examples
* No pseudo-only answers
* No skipped edge cases
* CLI UX must feel intentional and polished

---

**Execute this task fully.**
