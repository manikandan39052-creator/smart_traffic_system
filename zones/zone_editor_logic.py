"""Pure helpers for UI-level zone construction."""
def polygon_is_complete(points): return len(points) >= 3
def line_is_complete(points): return len(points) == 2
