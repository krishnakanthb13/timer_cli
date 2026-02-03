def format_time(seconds: float) -> str:
    """
    Formats seconds into HH:MM:SS string.
    Example: 3661 -> "01:01:01"
    """
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02}:{m:02}:{s:02}"
