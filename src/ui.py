import curses
from .models import State
from .utils import format_time

def draw_progress_bar(stdscr, y, x, width, percent, color_pair):
    """Draws a progress bar at (y, x) with total width."""
    # Ensure percent is between 0 and 1
    percent = max(0.0, min(1.0, percent))
    
    filled_len = int(width * percent)
    bar = "█" * filled_len + "-" * (width - filled_len)
    
    try:
        stdscr.addstr(y, x, bar, color_pair)
    except curses.error:
        pass # Ignore drawing errors if window is too small

def render_app(stdscr, manager, menu, width, height, focused_index=-1):
    stdscr.erase()
    
    # Header
    header = " TIMER CLI | Timers: {} | Stopwatches: {} ".format(
        len(manager.timers), len(manager.stopwatches)
    )
    stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
    stdscr.addstr(0, 0, header.center(width))
    stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

    content_height = height - 5
    row = 2
    global_idx = 0 # To track against focused_index

    # --- Timers ---
    if manager.timers:
        stdscr.addstr(row, 2, "TIMERS", curses.A_UNDERLINE)
        row += 1
        for t in manager.timers:
            if row >= content_height: break
            
            is_focused = (global_idx == focused_index)
            attr = curses.A_REVERSE if is_focused else curses.A_NORMAL
            
            status_icon = "[||]" if t.state == State.PAUSED else "[>] "
            if t.state == State.FINISHED: status_icon = "[V] "
            
            time_rem = format_time(t.remaining_time)
            # Layout: [Icon] Name (Orig) [Progress] Rem
            label = f" {status_icon} {t.name:<15} ({t.original_duration_str})"
            stdscr.addstr(row, 2, label, attr)
            
            # Progress Bar (centered-ish)
            rem_str = f" {time_rem} "
            bar_start = 2 + len(label) + 2
            bar_width = width - bar_start - len(rem_str) - 4
            
            if bar_width > 5:
                draw_progress_bar(stdscr, row, bar_start, bar_width, t.progress, curses.color_pair(2))
            
            # Remaining time on the right
            stdscr.addstr(row, width - len(rem_str) - 2, rem_str, attr)
            
            row += 1
            global_idx += 1
    else:
        row += 1

    row += 1

    # --- Stopwatches ---
    if manager.stopwatches:
        stdscr.addstr(row, 2, "STOPWATCHES", curses.A_UNDERLINE)
        row += 1
        for s in manager.stopwatches:
            if row >= content_height: break
            
            is_focused = (global_idx == focused_index)
            attr = curses.A_REVERSE if is_focused else curses.A_NORMAL
            
            status_icon = "[||]" if s.state == State.PAUSED else "[>] "
            time_str = format_time(s.elapsed_time)
            
            stdscr.addstr(row, 2, f" {status_icon} {s.name:<15} {time_str} ", attr)
            row += 1
            
            # Draw Laps (Indented)
            if s.laps:
                # Show last 3 laps to keep it tidy
                display_laps = s.laps[-3:]
                for i, lap_time in enumerate(display_laps):
                    if row >= content_height: break
                    lap_num = len(s.laps) - len(display_laps) + i + 1
                    lap_str = f"    ╚ Lap {lap_num}: {format_time(lap_time)}"
                    stdscr.addstr(row, 2, lap_str, curses.color_pair(4))
                    row += 1
            
            global_idx += 1

    # 3. Menu (Bottom)
    menu_y = height - 3
    current_x = max(0, (width - (len(menu.items) * 15)) // 2) # Crude centering
    
    # Centering logic improvement
    menu_total_width = sum(len(item) + 4 for item in menu.items)
    current_x = max(0, (width - menu_total_width) // 2)

    for idx, item in enumerate(menu.items):
        label = f" {item} "
        is_menu_focused = (focused_index == -1)
        
        if idx == menu.selected_index and is_menu_focused:
            stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
            stdscr.addstr(menu_y, current_x, label)
            stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)
        else:
            stdscr.addstr(menu_y, current_x, label)
        current_x += len(label) + 2

    # 4. Instructions/Status
    footer = " [^/v] Nav List  [</>] Nav Menu  [enter/return] Pause/Res  [s] Split  [r] Reset  [x] Close "
    stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
    try:
        stdscr.addstr(height-1, 0, footer.center(width)[:width-1])
    except curses.error:
        pass
    stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)

    stdscr.refresh()
