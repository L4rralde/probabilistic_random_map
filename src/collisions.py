import sys

import numpy as np

from shapes import Segment, Point, Polygon


EPS = sys.float_info.epsilon

def lines_intersect(line_1: Segment, line_2: Segment) -> bool:
    if line_1.points[0] in line_2.points:
        return False
    if line_1.points[1] in line_2.points:
        return False

    x1, y1 = line_1.points[0].x, line_1.points[0].y
    x2, y2 = line_1.points[1].x, line_1.points[1].y
    x3, y3 = line_2.points[0].x, line_2.points[0].y
    x4, y4 = line_2.points[1].x, line_2.points[1].y

    m1 = (y1 - y2)/(x1 - x2 + EPS)
    m2 = (y3 - y4)/(x3 - x4 + EPS)
    if m1 == m2:
        return False

    b1 = y1 - m1*x1
    b2 = y3 - m2*x3

    xa = (b2 - b1)/(m1 - m2)

    low_1 = min(x1, x2)
    high_1 = max(x1, x2)

    if not low_1 - EPS < xa < high_1 + EPS:
        return False
    low_2 = min(x3, x4)
    high_2 = max(x3, x4)
    if not low_2 - EPS < xa < high_2 + EPS:
        return False
    return True

def point_insise_boundingbox(point: Point, polygon: Polygon) -> bool:
    xcoords = [vertex.x for vertex in polygon.points]
    ycoords = [vertex.y for vertex in polygon.points]
    return (
        min(xcoords) < point.x < max(xcoords) and
        min(ycoords) < point.y < max(ycoords)
    )

def bounding_box_overlaps(polygon_a: Polygon, polygon_b: Polygon) -> bool:
    if len(polygon_a.points) < len(polygon_b.points):
        simple_polygon = polygon_a
        hard_polygon = polygon_b
    else:
        simple_polygon = polygon_b
        hard_polygon = polygon_b

    xcoords = [vertex.x for vertex in hard_polygon.points]
    ycoords = [vertex.y for vertex in hard_polygon.points]
    minx, maxx = min(xcoords), max(xcoords)
    miny, maxy = min(ycoords), max(ycoords)

    for point in simple_polygon.points:
        if minx < point.x < miny and miny < point.y < maxy:
            return True
    return False


def segment_intersects_polygon(segment: Segment, polygon: Polygon) -> bool:
    n_vertices = len(polygon.points)
    for i in range(n_vertices):
        end_a = polygon.points[i]
        end_b = polygon.points[(i + 1) % n_vertices]
        edge = Segment(end_a, end_b)
        if lines_intersect(segment, edge):
            return True
    return False


def segment_intersects(segment: Segment, polygons: list) -> bool:
    intersections = (
        segment_intersects_polygon(segment, polygon)
        for polygon in polygons
    )
    return any(intersections)


def ray_casting(point: Point, polygon: Polygon, eps: float = 0.01) -> bool:
    xcoords = [vertex.x for vertex in polygon.points]
    ycoords = [vertex.y for vertex in polygon.points]
    ray = Segment(
        point,
        Point(max(xcoords) + eps, max(ycoords) + eps)
    )
    n_intersects = 0
    n_vertices = len(polygon.points)
    for i in range(n_vertices):
        end_a = polygon.points[i]
        end_b = polygon.points[(i + 1) % n_vertices]
        edge = Segment(end_a, end_b)
        if lines_intersect(ray, edge):
            n_intersects += 1
    return n_intersects % 2 == 1


def get_point_to_segment_distance(point: Point, segment: Segment) -> float:
    #line
    y1, y2 = segment.points[0].y, segment.points[1].y
    x1, x2 = segment.points[0].x, segment.points[1].x
    # ax + by + c = 0
    a = y1 - y2
    b = x2 - x1
    c = x1*y2 - x2*y1
    #point
    x0, y0 = point.x, point.y
    #Get closest point to (x0, y0) in line
    x = (b*b*x0 - b*a*y0 - a*c)/(a*a + b*b)
    y = (-a*b*x0 + a*a*y0 - b*c)/(a*a + b*b)

    x = max(x, min(x1, x2))
    x = min(x, max(x1, x2))

    y = max(y, min(y1, y2))
    y = min(y, max(y1, y2))

    return ((x - x0)**2 + (y - y0)**2)**0.5


def point_collides_with_polygon(
        point: Point,
        polygon: Polygon,
        th: float
    ) -> bool:
    if ray_casting(point, polygon):
        return True
    n_vertices = len(polygon.points)
    for i in range(n_vertices):
        end_a = polygon.points[i]
        end_b = polygon.points[(i + 1) % n_vertices]
        edge = Segment(end_a, end_b)
        dist = get_point_to_segment_distance(point, edge)
        if dist < th:
            return True
    return False


def point_collides(point: Point, polygons: list, th: float) -> bool:
    collisions = (
        point_collides_with_polygon(
            point,
            polygon,
            th
        )
        for polygon in polygons
    )
    return any(collisions)


def segment_collides(segment: Segment, polygons: list, th: float) -> bool:
    start = segment.points[0]
    goal = segment.points[1]
    m = (goal.y - start.y)/(goal.x - start.x)
    b = start.y - m*start.x
    nintervals = int(segment.len()/0.01)
    ray_xs = np.linspace(start.x, goal.x, nintervals)
    ray_ys = m*ray_xs + b
    possible_confs = (Point(x, y) for x, y in zip(ray_xs, ray_ys))
    possible_collisions = (
        point_collides(point, polygons, th)
        for point in possible_confs
    )
    return any(possible_collisions)
