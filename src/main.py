import curses
import time
import sys
from .managers import TimeManager
from .ui import render_app
from .logging_setup import setup_logging, log_action, get_log_path
from .models import State, Timer, Stopwatch

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
            
        view_mode = "Grouped" # Toggle with TAB
        offset = 0
        
        while True:
            stdscr.erase()
            h, w = stdscr.getmaxyx()
            
            # Header
            title = f" HISTORY ({view_mode}) - TAB to toggle, 'q' to back "
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(0, 0, title.center(w))
            stdscr.attroff(curses.color_pair(1))
            
            display_lines = []
            display_lines.append("") # Vertical space for consistency
            if view_mode == "Raw":
                display_lines = [l.strip() for l in lines]
            else:
                # Grouping logic
                groups = {} # id -> {info, events}
                system_events = []
                
                import re
                # Pattern: 2026-02-03 17:34:22 [INFO] [Category] Action - Details
                pattern = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[INFO\] \[([^\]]+)\] ([^-]+)- (.*)')
                
                for line in lines:
                    match = pattern.search(line)
                    if not match: continue
                    ts, cat, action, details = match.groups()
                    action = action.strip()
                    details = details.strip()
                    
                    if cat == "System":
                        system_events.append(f"  {ts} > {action} {details}")
                        continue
                        
                    # Find ID and Name in details
                    id_match = re.search(r'ID: ([a-f0-9]+)', details)
                    name_match = re.search(r'Name: ([^,]+)', details)
                    
                    obj_id = id_match.group(1) if id_match else "Unknown"
                    obj_name = name_match.group(1).strip() if name_match else None
                    
                    # If this is a 'Started' event without an ID (legacy), 
                    # we use a pseudo-id based on name to keep it separate from other "Unknowns"
                    effective_id = obj_id
                    if obj_id == "Unknown" and action == "Started" and obj_name:
                        effective_id = f"legacy_{obj_name}"

                    if effective_id not in groups:
                        groups[effective_id] = {
                            "id": obj_id, 
                            "type": cat, 
                            "name": "Unknown", 
                            "events": [], 
                            "last_ts": ts
                        }
                    
                    if obj_name:
                        groups[effective_id]["name"] = obj_name
                    
                    # Clean details for display (remove ID: xxx since it's in header)
                    clean_details = re.sub(r'ID: [a-f0-9]+', '', details).strip()
                    clean_details = clean_details.strip(',').strip()
                    
                    display_action = f"{action} {clean_details}".strip()
                    groups[effective_id]["events"].append(f"  {ts} > {display_action}")
                    groups[effective_id]["last_ts"] = ts

                # Sort groups by latest timestamp
                sorted_groups = sorted(groups.values(), key=lambda x: x["last_ts"], reverse=True)
                
                for g in sorted_groups:
                    name_display = g['name']
                    id_display = f" (ID: {g['id']})" if g['id'] != "Unknown" else ""
                    header = f"[{g['type']}] {name_display}{id_display}"
                    
                    display_lines.append(header)
                    for e in reversed(g["events"]):
                        display_lines.append(e)
                    display_lines.append("-" * (w-2))
                
                if system_events:
                    display_lines.append("[SYSTEM EVENTS]")
                    display_lines.extend(reversed(system_events))
                    display_lines.append("-" * (w-2))

            # Render display_lines with scrolling
            max_lines = h - 2
            start_idx = offset
            end_idx = min(len(display_lines), offset + max_lines)
            
            view_content = display_lines[start_idx:end_idx]
            
            for i, line in enumerate(view_content):
                if line.startswith("["): # Category headers
                    stdscr.attron(curses.A_BOLD | curses.color_pair(2))
                    stdscr.addstr(i+1, 1, line[:w-2])
                    stdscr.attroff(curses.A_BOLD | curses.color_pair(2))
                else:
                    stdscr.addstr(i+1, 1, line[:w-2])
                
            stdscr.refresh()
            
            # Wait for key
            stdscr.nodelay(False)
            k = stdscr.getch()
            stdscr.nodelay(True)
            
            if k == ord('q') or k == 27:
                break
            elif k == ord('\t'): # TAB
                view_mode = "Raw" if view_mode == "Grouped" else "Grouped"
                offset = 0
            elif k == curses.KEY_UP:
                offset = max(0, offset - 1)
            elif k == curses.KEY_DOWN:
                offset = min(len(display_lines) - max_lines, offset + 1) if len(display_lines) > max_lines else 0

    def handle_new_stopwatch(self, stdscr):
        name = self.get_user_input(stdscr, "Name (optional, max 15 char): ")
        if name is None: return # Cancelled
        
        self.manager.add_stopwatch(name)

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
