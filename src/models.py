import time
import uuid
from enum import Enum
from typing import List, Optional

class State(Enum):
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    FINISHED = "FINISHED"
    IDLE = "IDLE"  # Initial state for Stopwatch

from .utils import format_time

class Timer:
    def __init__(self, duration_seconds: int, name: str):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.duration = duration_seconds
        self.original_duration_str = format_time(duration_seconds) # To show on left
        self.pause_time: Optional[float] = None
        self.accumulated_pause: float = 0.0
        self.state = State.RUNNING # Auto-starts on creation usually, or we can make it explicit
        self.notified = False
        
        # Start immediately upon creation for this CLI's UX
        self.start()

    def start(self):
        self.start_time = time.time()
        self.state = State.RUNNING

    def pause(self):
        if self.state == State.RUNNING:
            self.pause_time = time.time()
            self.state = State.PAUSED

    def resume(self):
        if self.state == State.PAUSED:
            now = time.time()
            self.accumulated_pause += (now - self.pause_time)
            self.pause_time = None
            self.state = State.RUNNING

    def stop(self):
        self.state = State.FINISHED

    def reset(self):
        self.start_time = time.time()
        self.pause_time = None
        self.accumulated_pause = 0.0
        self.state = State.RUNNING
        self.notified = False

    @property
    def remaining_time(self) -> float:
        if self.state == State.FINISHED:
            return 0.0
        
        if self.start_time is None:
            return float(self.duration)

        now = time.time()
        if self.state == State.PAUSED:
            now = self.pause_time

        elapsed = now - self.start_time - self.accumulated_pause
        remaining = self.duration - elapsed
        
        if remaining <= 0:
            self.state = State.FINISHED
            return 0.0
        
        return remaining

    @property
    def progress(self) -> float:
        """Returns 0.0 to 1.0 representing completion."""
        if self.duration == 0:
            return 1.0
        rem = self.remaining_time
        return 1.0 - (rem / self.duration)

class Stopwatch:
    def __init__(self, name: str):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.start_time: Optional[float] = None
        self.pause_time: Optional[float] = None
        self.accumulated_pause: float = 0.0
        self.laps: List[float] = [] # timestamps of laps
        self.state = State.RUNNING # Auto-start
        
        self.start()

    def start(self):
        self.start_time = time.time()
        self.state = State.RUNNING

    def pause(self):
        if self.state == State.RUNNING:
            self.pause_time = time.time()
            self.state = State.PAUSED

    def resume(self):
        if self.state == State.PAUSED:
            now = time.time()
            self.accumulated_pause += (now - self.pause_time)
            self.pause_time = None
            self.state = State.RUNNING

    def reset(self):
        self.start_time = time.time()
        self.pause_time = None
        self.accumulated_pause = 0.0
        self.laps = []
        self.state = State.RUNNING

    def lap(self):
        if self.state == State.RUNNING:
            self.laps.append(self.elapsed_time)

    @property
    def elapsed_time(self) -> float:
        if self.start_time is None:
            return 0.0

        now = time.time()
        if self.state == State.PAUSED:
            now = self.pause_time

        return now - self.start_time - self.accumulated_pause
