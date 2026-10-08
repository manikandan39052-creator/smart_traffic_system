from datetime import datetime
def utc_now_iso(): return datetime.now().astimezone().isoformat()
