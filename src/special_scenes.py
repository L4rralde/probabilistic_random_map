import pygame

from scene.scenes import Point, GLScene, GLUtils
from shapes import Polygon, Circle
from prm import ProbabilisticRandomMap


class Blinker:
    def __init__(self, to_call: object, period: int = 16, **kwargs) -> None:
        self.period = period
        self.cycle = 0
        self.to_call = to_call
        self.call = False
        self.kwargs = kwargs

    def blink(self) -> None:
        if self.cycle == 0:
            self.call = not self.call
        self.cycle = (self.cycle + 1) % self.period
        if self.call:
            self.to_call(**self.kwargs)

default_polygons = [
    Polygon([[-0.8, 0.2], [-0.6, 0.6], [-0.5, 0.4], [-0.15, 0.27]]),
    Polygon([[-0.5, -0.6], [-0.8, -0.6], [-0.2, -0.4], [-0.46, -0.92]]),
    Polygon([[0.33, -0.12], [0, -0.2], [0.2, 0.2], [0.4, 0.04], [0.8, 0.2], [0.62, -0.27]])
]

patologycal_grid = [
    Polygon([[-0.75, -0.4], [-0.7, 0.4], [-0.5, 0.4], [-0.45, -0.4]]),
    Polygon([[-0.15, -0.4], [-0.2, 0.4], [0.2, 0.4], [0.15, -0.4]]),
    Polygon([[0.45, -0.4], [0.5, 0.4], [0.7, 0.4], [0.75, -0.4]]),
]


class PolygonScene(GLScene):
    def __init__(
            self,
            title: str,
            width: int,
            height: int,
            max_fps: int = 60,
            thopological: bool = False,
            **kwargs
        ) -> None:
        super().__init__(title, width, height, max_fps, **kwargs)
        polygons = patologycal_grid if thopological else default_polygons
        self.polygons = kwargs.get("polygons", polygons)

    def render(self) -> None:
        super().render()
        for polygon in self.polygons:
            polygon.draw(
                edge_color = (72/255, 116/255, 191/255, 1.0),
                draw_points = False,
            )


class PrmScene(PolygonScene):
    def __init__(self, title: str, width: int, height: int, max_fps: int = 60, **kwargs) -> None:
        super().__init__(title, width, height, max_fps, **kwargs)
        self.start = Circle(Point(0, 0), 0.03)
        self.goal = Point(-0.5, 0)
        self.pause = True
        self.prm = ProbabilisticRandomMap(
            self.polygons,
            self.start.radius,
            self.start.center,
            self.goal
        )
        self.update_cycle = 0
        self.blinker = Blinker(
            lambda **kwargs: GLUtils.draw_points([self.goal], **kwargs),
            period = 6,
            size = 25,
            color = (212/255, 0, 120/255, 1.0)
        )

    def get_inputs(self) -> None:
        super().get_inputs()
        for event in self.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.pause = not self.pause
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                screen_point = Point(x, y)
                ortho = self.to_ortho(screen_point)
                ortho.y *= -1
                if event.button == 1: #Left click
                    self.start.center = ortho
                    self.prm.reset(self.start.center, self.goal)
                if event.button == 3: #Right click
                    self.goal = ortho
                    self.prm.reset(self.start.center, self.goal)

    def update(self) -> None:
        super().update()
        if self.pause:
            return
        self.prm.update()

    def render(self) -> None:
        super().render()
        for segment in self.prm.edges:
            segment.draw(color = (1.0, 0.8, 0.5, 1.0))
        if self.prm.shortest_path:
            self.prm.shortest_path.draw(color = (1.0, 0, 0, 1.0))
        for milestone in self.prm.milestones:
            vertex = Circle(milestone, 0.015)
            vertex.draw(color = (220/255, 88/255, 88/255, 1.0))
        self.blinker.blink()
        self.start.draw(color = (251/255, 20/255, 0, 1.0))
