"""Coordinate primitives. All rule checks use vehicle bottom-centre points."""
from __future__ import annotations
from typing import Sequence

Point = tuple[float, float]

def bottom_center(box: Sequence[float]) -> Point:
    x1, _y1, x2, y2 = box
    return ((x1 + x2) / 2, y2)

def point_in_polygon(point: Point, polygon: Sequence[Sequence[float]]) -> bool:
    if len(polygon) < 3: return False
    x, y = point; inside = False
    for i in range(len(polygon)):
        x1, y1 = polygon[i - 1]; x2, y2 = polygon[i]
        if (y1 > y) != (y2 > y) and x < (x2-x1) * (y-y1) / ((y2-y1) or 1e-12) + x1:
            inside = not inside
    return inside

def _orient(a: Point, b: Point, c: Point) -> float:
    return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])

def segments_intersect(a: Point, b: Point, c: Point, d: Point) -> bool:
    o1, o2, o3, o4 = _orient(a,b,c), _orient(a,b,d), _orient(c,d,a), _orient(c,d,b)
    return (o1 > 0) != (o2 > 0) and (o3 > 0) != (o4 > 0)

def crosses_line(previous: Point | None, current: Point, line: Sequence[Sequence[float]]) -> bool:
    return previous is not None and len(line) == 2 and segments_intersect(previous, current, tuple(line[0]), tuple(line[1]))
