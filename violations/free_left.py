from zones.geometry import point_in_polygon
class FreeLeftRule:
    def __init__(self): self.emitted=set()
    def check(self, track_id, current, zone_id, polygon):
        key=(track_id,zone_id)
        if key not in self.emitted and point_in_polygon(current,polygon): self.emitted.add(key); return True
        return False
