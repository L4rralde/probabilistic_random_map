from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

from scene.scenes import Point, GLUtils

class Segment:
    def __init__(self, point_i: Point, point_j: Point) -> None:
        self.points = [point_i, point_j]
    
    def draw(self, **kwargs) -> None:
        GLUtils.draw_line(self.points, **kwargs)

    def len(self) -> float:
        return (
            (self.points[0].x - self.points[1].x)**2 +
            (self.points[0].y - self.points[1].y)**2
        )**0.5

    @property
    def displacement(self) -> list:
        return [
            self.points[1].y - self.points[0].y,
            self.points[1].x - self.points[0].x
        ]

    @property
    def angle(self) -> float:
        return np.arctan2(
            self.points[1].y - self.points[0].y,
            self.points[1].x - self.points[0].x
        )

class Polygon:
    def __init__(self, points: list) -> None:
        if type(points[0]) == Point:
            self.points = points
        elif type(points[0]) == list:
            self.points = [Point(*point) for point in points]
        else:
            raise RuntimeError("Not recgonized data type")
        self.len = len(self.points)

    def draw(self, **kwargs) -> None:
        GLUtils.draw_polygon(self.points, **kwargs)


class Path:
    def __init__(self, points: list) -> None:
        self.points = points

    def draw(self, **kwargs) -> None:
        GLUtils.draw_line(
            self.points,
            **kwargs
        )

    def __getitem__(self, idx: int) -> Point:
        return self.points[idx]

    def __repr__(self) -> str:
        points_strs = [str(point) for point in self.points]
        return ", ".join(points_strs)


class Circle:
    def __init__(self, center: Point, radius: float) -> None:
        self.center = center
        self.radius = radius

    def draw(self, **kwargs) -> None:
        thetas = np.linspace(0, 2*np.pi, 100)
        points = [
            Point(
                self.center.x + self.radius*np.cos(theta),
                self.center.y + self.radius*np.sin(theta)
            )
            for theta in thetas
        ]
        if "color" in kwargs:
            kwargs["edge_color"] = kwargs.pop("color")
        GLUtils.draw_polygon(points, draw_points=False, **kwargs)
