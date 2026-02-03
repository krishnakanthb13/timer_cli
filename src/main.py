import curses
import time
import sys
import re
from datetime import datetime
from .managers import TimeManager
from .ui import render_app
from .logging_setup import setup_logging, log_action, get_log_path
from .models import State, Timer, Stopwatch

def build_grouped_view(log_lines, width):
    groups = {} # id -> {info, events}
    system_events = []
    pattern = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[([A-Z]+)\] \[([^\]]+)\] ([^-]+)- (.*)')
    
    for line in log_lines:
        match = pattern.search(line)
        if not match: continue
        ts, level, cat, action, details = match.groups()
        action, details = action.strip(), details.strip()
        
        if cat == "System":
            system_events.append(f"  {ts} > {action} {details}")
            continue
            
        id_match = re.search(r'ID: ([a-f0-9]+)', details)
        name_match = re.search(r'Name: ([^,]+)', details)
        obj_id = id_match.group(1) if id_match else "Unknown"
        obj_name = name_match.group(1).strip() if name_match else None
        
        effective_id = obj_id
        if obj_id == "Unknown" and action == "Started" and obj_name:
            effective_id = f"legacy_{obj_name}"

        if effective_id not in groups:
            groups[effective_id] = {
                "id": obj_id, "type": cat, "name": "Unknown", 
                "events": [], "last_ts": ts, "start_ts": ts, "lap_count": 0
            }
        
        if action == "Started": groups[effective_id]["start_ts"] = ts
        if obj_name: groups[effective_id]["name"] = obj_name
        
        clean_details = re.sub(r'ID: [a-f0-9]+', '', details).strip().strip(',').strip()
        
        # Calculate +Time from start
        try:
            fmt = "%Y-%m-%d %H:%M:%S"
            delta = datetime.strptime(ts, fmt) - datetime.strptime(groups[effective_id]["start_ts"], fmt)
            h, rem = divmod(int(delta.total_seconds()), 3600)
            m, s = divmod(rem, 60)
            delta_str = f"+{h:02}:{m:02}:{s:02}"
        except (ValueError, TypeError, KeyError):
            delta_str = "+00:00:00"

        if action == "Lap":
            groups[effective_id]["lap_count"] += 1
            display_action = f"Lap {groups[effective_id]['lap_count']}"
            if clean_details: display_action += f": {clean_details}"
        else:
            display_action = f"{action} {clean_details}".strip()
        
        groups[effective_id]["events"].append(f"  {ts} ({delta_str}) > {display_action}")
        groups[effective_id]["last_ts"] = ts

    display = [""]
    sorted_groups = sorted(groups.values(), key=lambda x: x["last_ts"], reverse=True)
    for g in sorted_groups:
        id_display = f" (ID: {g['id']})" if g['id'] != "Unknown" else ""
        display.append(f"[{g['type']}] {g['name']}{id_display}")
        display.extend(g["events"])
        display.append("-" * (width - 2))
    
    if system_events:
        display.append(""); display.append("[SYSTEM EVENTS]")
        display.extend(reversed(system_events))
        display.append("-" * (width - 2))
    return display

class Menu:
    def __init__(self, items):
        self.items = items
        self.selected_index = 0

    def next(self):
        self.selected_index = (self.selected_index + 1) % len(self.items)

    def prev(self):
        self.selected_index = (self.selected_index - 1) % len(self.items)
    
    @property
    def current_item(self):
        return self.items[self.selected_index]

class App:
    def __init__(self):
        self.manager = TimeManager()
        self.menu = Menu(["New Timer", "New Stopwatch", "Control Active", "History", "Exit"])
        self.running = True
        self.list_index = -1 # -1 means focus is on the bottom menu

    def get_all_items(self):
        return self.manager.timers + self.manager.stopwatches

    def handle_input(self, key, stdscr):
        all_items = self.get_all_items()
        
        if key == curses.KEY_RIGHT:
            self.menu.next()
        elif key == curses.KEY_LEFT:
            self.menu.prev()
            
        elif key == curses.KEY_UP:
            if self.list_index == -1: # From menu to last item of list
                if all_items:
                    self.list_index = len(all_items) - 1
            else:
                self.list_index -= 1 # Move up in list, -1 will go to menu
                
        elif key == curses.KEY_DOWN:
            if self.list_index < len(all_items) - 1:
                self.list_index += 1
            else:
                self.list_index = -1 # Go back to menu
                
        elif key in [10, 13, curses.KEY_ENTER, 459]: # Enter
            if self.list_index == -1:
                self.execute_menu_action(stdscr)
            else:
                # Toggle pause/resume on the selected item
                self.toggle_selected_item()
                
        elif key == ord('s') or key == ord('S'): # Split / Lap
            self.lap_selected_item()
        elif key == ord('r') or key == ord('R'): # Reset
            self.reset_selected_item()
        elif key == ord('d') or key == ord('D'): # Delete / Remove
            self.remove_selected_item()
        elif key == ord('q'):
            self.running = False

    def toggle_selected_item(self):
        all_items = self.get_all_items()
        if 0 <= self.list_index < len(all_items):
            item = all_items[self.list_index]
            if item.state == State.PAUSED:
                item.resume()
                log_action(type(item).__name__, "Resume", f"ID: {item.id}")
            else:
                item.pause()
                log_action(type(item).__name__, "Pause", f"ID: {item.id}")

    def reset_selected_item(self):
        all_items = self.get_all_items()
        if 0 <= self.list_index < len(all_items):
            item = all_items[self.list_index]
            item.reset()
            log_action(type(item).__name__, "Reset", f"ID: {item.id}")

    def lap_selected_item(self):
        all_items = self.get_all_items()
        if 0 <= self.list_index < len(all_items):
            item = all_items[self.list_index]
            if isinstance(item, Stopwatch):
                item.lap()
                log_action("Stopwatch", "Lap", f"ID: {item.id}")
        else:
            # Fallback to current behavior if nothing selected
            self.manager.lap_active()

    def remove_selected_item(self):
        all_items = self.get_all_items()
        if 0 <= self.list_index < len(all_items):
            item = all_items[self.list_index]
            if isinstance(item, Timer):
                self.manager.remove_timer(item)
            else:
                self.manager.remove_stopwatch(item)
            # Adjust index
            if self.list_index >= len(self.get_all_items()):
                self.list_index = len(self.get_all_items()) - 1

    def execute_menu_action(self, stdscr):
        action = self.menu.current_item
        if action == "Exit":
            self.running = False
        elif action == "New Timer":
            self.handle_new_timer(stdscr)
        elif action == "New Stopwatch":
            self.handle_new_stopwatch(stdscr)
        elif action == "Control Active":
            self.manager.toggle_all_pause()
        elif action == "History":
            self.show_history(stdscr)

    def get_user_input(self, stdscr, prompt):
        """Helper to get non-blocking strings from user."""
        input_str = ""
        stdscr.nodelay(False)
        try:
            while True:
                stdscr.erase()
                height, width = stdscr.getmaxyx()
                render_app(stdscr, self.manager, self.menu, width, height, self.list_index)
                
                # Draw Prompt Overlay
                stdscr.attron(curses.color_pair(3))
                # Position input box roughly in the middle
                y, x = 10, 5
                stdscr.addstr(y, x, prompt + input_str + "_")
                stdscr.attroff(curses.color_pair(3))
                stdscr.refresh()
                
                key = stdscr.getch()
                if key in [10, 13, curses.KEY_ENTER, 459]:
                    return input_str.strip()
                elif key in [8, 127, curses.KEY_BACKSPACE]:
                    input_str = input_str[:-1]
                elif key == 27: # Esc
                    return None
                elif 32 <= key <= 126:
                    if len(input_str) < 30: # Hard limit for input
                        input_str += chr(key)
        finally:
            stdscr.nodelay(True)

    def handle_new_timer(self, stdscr):
        dur_str = self.get_user_input(stdscr, "Duration [HH MM SS] or [HH MM] or [MM]: ")
        if dur_str is None: return
        
        # Try to parse duration immediately to see if it's valid
        total_seconds = 0
        try:
            parts = dur_str.split()
            if len(parts) == 3: # HH MM SS
                h, m, s = map(int, parts)
                total_seconds = h*3600 + m*60 + s
            elif len(parts) == 2: # HH MM
                h, m = map(int, parts)
                total_seconds = h*3600 + m*60
            elif len(parts) == 1: # MM
                m = int(parts[0])
                total_seconds = m*60
        except ValueError:
            return

        if total_seconds <= 0: return

        name = self.get_user_input(stdscr, "Name (optional, max 15 char): ")
        if name is None: return # Cancelled
        
        self.manager.add_timer(total_seconds, name)

    def handle_new_stopwatch(self, stdscr):
        name = self.get_user_input(stdscr, "Name (optional, max 15 char): ")
        if name is None: return # Cancelled
        
        self.manager.add_stopwatch(name)

    def show_history(self, stdscr):
        # Blocking view for history
        log_path = get_log_path()
        try:
            with open(log_path, "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            lines = ["No logs found."]

        # Pre-calculated content helpers
        # Initial calculation
        view_mode = "Grouped" 
        offset = 0
        h, w = stdscr.getmaxyx()
        last_w = w
        
        views = {
            "Raw": [""] + [l.strip() for l in reversed(lines)],
            "Grouped": build_grouped_view(lines, w)
        }
        
        while True:
            stdscr.erase()
            h, w = stdscr.getmaxyx()
            
            # Rebuild if resized
            if w != last_w:
                views["Grouped"] = build_grouped_view(lines, w)
                last_w = w
                
            display_lines = views[view_mode]
            
            # Header
            title = f" HISTORY ({view_mode}) - [TAB] Toggle | [q] Back "
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(0, 0, title.center(w))
            stdscr.attroff(curses.color_pair(1))
            
            # Rendering
            max_lines = h - 2
            view_content = display_lines[offset : offset + max_lines]
            for i, line in enumerate(view_content):
                if line.startswith("["): # Category headers
                    stdscr.attron(curses.A_BOLD | curses.color_pair(2))
                    stdscr.addstr(i+1, 1, line[:w-2])
                    stdscr.attroff(curses.A_BOLD | curses.color_pair(2))
                else:
                    stdscr.addstr(i+1, 1, line[:w-2])
            stdscr.refresh()
            
            # Input
            stdscr.nodelay(False)
            k = stdscr.getch()
            stdscr.nodelay(True)
            
            if k == ord('q') or k == 27: break
            elif k == ord('\t'):
                view_mode = "Raw" if view_mode == "Grouped" else "Grouped"
                offset = 0
            elif k == curses.KEY_UP:
                offset = max(0, offset - 1)
            elif k == curses.KEY_DOWN:
                offset = min(len(display_lines) - max_lines, offset + 1) if len(display_lines) > max_lines else offset
            elif k == curses.KEY_PPAGE: # Page Up
                offset = max(0, offset - max_lines)
            elif k == curses.KEY_NPAGE: # Page Down
                offset = min(len(display_lines) - max_lines, offset + max_lines) if len(display_lines) > max_lines else offset


def main():
    setup_logging()
    
    # Wrapper handles initialization and cleanup safely
    curses.wrapper(run_app)

def run_app(stdscr):
    # Setup colors
    curses.curs_set(0) # Hide cursor
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)  # Header
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK) # Progress Bar
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_CYAN)  # Selected Menu
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK) # Normal text
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLUE)   # Footer / Status Bar (Blue/White)

    app = App()
    stdscr.keypad(True) # Ensure special keys are handled
    stdscr.nodelay(True) # Non-blocking input

    while app.running:
        # Input
        try:
            key = stdscr.getch()
        except:
            key = -1

        if key != -1:
            app.handle_input(key, stdscr)

        # Update
        app.manager.update()

        # Render
        height, width = stdscr.getmaxyx()
        render_app(stdscr, app.manager, app.menu, width, height, app.list_index)

        time.sleep(0.05) # Cap at ~20 FPS

if __name__ == "__main__":
    main()
