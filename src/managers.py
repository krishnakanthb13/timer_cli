from typing import List
from .models import Timer, Stopwatch, State
from .logging_setup import log_action

class TimeManager:
    def __init__(self):
        self.timers: List[Timer] = []
        self.stopwatches: List[Stopwatch] = []
        self.timer_count = 0
        self.stopwatch_count = 0

    def add_timer(self, duration: int, name: str = ""):
        self.timer_count += 1
        if not name:
            name = f"Timer {self.timer_count}"
        
        new_timer = Timer(duration, name[:15]) # Cap name
        self.timers.append(new_timer)
        log_action("Timer", "Started", f"Name: {new_timer.name}, Duration: {duration}s")
        return new_timer

    def add_stopwatch(self, name: str = ""):
        self.stopwatch_count += 1
        if not name:
            name = f"Stopwatch {self.stopwatch_count}"
            
        new_sw = Stopwatch(name[:15]) # Cap name
        self.stopwatches.append(new_sw)
        log_action("Stopwatch", "Started", f"Name: {new_sw.name}")
        return new_sw

    def remove_timer(self, timer: Timer):
        if timer in self.timers:
            self.timers.remove(timer)
            log_action("Timer", "Removed", f"ID: {timer.id}")

    def remove_stopwatch(self, sw: Stopwatch):
        if sw in self.stopwatches:
            self.stopwatches.remove(sw)
            log_action("Stopwatch", "Removed", f"ID: {sw.id}")

    def toggle_all_pause(self):
        """Pauses all if any are running, otherwise resumes all."""
        # Check if any are running
        any_running = any(t.state == State.RUNNING for t in self.timers) or \
                      any(s.state == State.RUNNING for s in self.stopwatches)
        
        if any_running:
            for t in self.timers: t.pause()
            for s in self.stopwatches: s.pause()
            log_action("System", "Control", "Paused All")
        else:
            for t in self.timers: t.resume()
            for s in self.stopwatches: s.resume()
            log_action("System", "Control", "Resumed All")

    def lap_active(self):
        """Records a lap for the most recently active stopwatch."""
        for sw in reversed(self.stopwatches):
            if sw.state == State.RUNNING:
                sw.lap()
                log_action("Stopwatch", "Lap", f"ID: {sw.id}, Lap Time: {sw.laps[-1]}")
                return True
        return False

    def update(self):
        """
        Called every tick. 
        Checks for finished timers to log them or trigger events.
        """
        for timer in self.timers:
            # Trigger state update if needed
            if timer.state == State.RUNNING:
                _ = timer.remaining_time # This property access updates state to FINISHED if time sets to 0
            
            # Check for completion event
            if timer.state == State.FINISHED and not timer.notified:
                timer.notified = True
                log_action("Timer", "Finished", f"ID: {timer.id}")
                from .sound import play_sound
                play_sound()
