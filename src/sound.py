import sys
import threading
import subprocess

def play_sound():
    """
    Plays a system alert sound in a non-blocking way (using threads).
    """
    threading.Thread(target=_beep, daemon=True).start()

def _beep():
    try:
        if sys.platform == "win32":
            import winsound
            # Plays the standard Windows "Exclamation" system sound
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        elif sys.platform == "darwin":
            # macOS
            subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"], check=False)
        else:
            # Linux / other - try terminal bell or generic beep
            print('\a')
    except Exception:
        pass 
