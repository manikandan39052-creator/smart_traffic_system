from zones.geometry import crosses_line
class StopLineRule:
    def __init__(self): self.emitted=set()
    def check(self, track_id, previous, current, line, signal_state):
        key=(track_id, tuple(map(tuple,line)))
        if signal_state == "RED" and key not in self.emitted and crosses_line(previous,current,line): self.emitted.add(key); return True
        return False
