import numpy as np

from scene.scenes import Point
import collisions
from prm import ProbabilisticRandomMap
from scene.scenes import GLUtils


class MonteCarloFreeVolume:
    def __init__(self, polygons: list) -> None:
        self.polygons = polygons
        self.free_pts = []
        self.non_free_pts = []
        self._last_volume = -1
        self._volume = -1

    def finished(self) -> bool:
        did_finish = (
            len(self.free_pts) > 1000 and
            abs(self._volume - self._last_volume) < 2e-4
        )
        return did_finish

    def sample(self, ntries: int = 5) -> None:
        new_samples = [
            Point(*array)
            for array in np.random.uniform(-1, 1, (ntries, 2))
        ]
        for sample in new_samples:
            if collisions.point_collides(sample, self.polygons, 0):
                self.non_free_pts.append(sample)
            else:
                self.free_pts.append(sample)
        
        num_free_pts = len(self.free_pts)
        num_non_free_pts = len(self.non_free_pts)

        self._last_volume = self._volume
        self._volume = num_free_pts/(num_free_pts + num_non_free_pts)

    def free_volume(self) -> float:
        return self._volume


class ProbabilisticRandomMapStar(ProbabilisticRandomMap):
    def __init__(
            self,
            polygons: list,
            radius: float,
            start: Point,
            goal: Point,
        ) -> None:
        super().__init__(polygons, radius, start, goal)
        self.free_volume_sampler = MonteCarloFreeVolume(polygons)
        self.state = "VOLUME"
        self.gamma = -1

    def update(self, th: float = 0.5, max_milestones: int = 200) -> bool:
        d = 2
        if self.state == "VOLUME":
            self.free_volume_sampler.sample(10)
            free_volume = self.free_volume_sampler.free_volume()
            print(f"Free volume: {free_volume: .4f}")
            if self.free_volume_sampler.finished():
                self.state = "PLANNING"
                self.gamma = 2 * ((1 + 1/d) * free_volume/np.pi)**(1/d)
        if self.state == "PLANNING":
            n = len(self.milestones)
            th = self.gamma * (np.log2(n)/n)**(1/d)
            super().update(th, max_milestones)
            print(f"n: {n}, radio: {th :.4f}, costo: {self.cost :.4f}")

    def draw(self) -> None:
        if self.state == "PLANNING":
            return super().draw()
        if self.state == "VOLUME":
            GLUtils.draw_points(
                self.free_volume_sampler.free_pts,
                color = (0.8, 0.1, 0.1, 1.0)
            )
            GLUtils.draw_points(
                self.free_volume_sampler.non_free_pts,
                color = (0.1, 0.8, 0.1, 1.0)
            )

    def finished(self) -> bool:
        return len(self.milestones) > 500
