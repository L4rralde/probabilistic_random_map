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
        did_finish = len(self.free_pts) + len(self.non_free_pts) > 10000
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
        self._volume = 4.0*num_free_pts/(num_free_pts + num_non_free_pts)

    def free_volume(self) -> float:
        return self._volume


class ProbabilisticRandomMapStar(ProbabilisticRandomMap):
    def __init__(
            self,
            polygons: list,
            radius: float,
            start: Point,
            goal: Point,
            n_samplles: int = 50,
            free_volume: float = None,
            **kwargs
        ) -> None:
        self.n_samples = n_samplles
        super().__init__(polygons, radius, start, goal)
        if free_volume is None:
            self.free_volume_sampler = MonteCarloFreeVolume(polygons)
            self.state = "VOLUME"
            self.free_volume = 0.0
            self.th = 0.0
        else:
            self.free_volume_sampler = None
            self.state = "PLANNING"
            self.free_volume = free_volume
            self.th = self.get_optimal_th(self.free_volume)

    def update(self, th: float = 0.5, max_milestones: int = 200) -> bool:
        if self.state == "VOLUME":
            self.free_volume_sampler.sample(10)
            if self.free_volume_sampler.finished():
                self.free_volume = self.free_volume_sampler.free_volume()
                print(f"Free volume: {self.free_volume: .4f}")
                self.state = "PLANNING"
                self.th = self.get_optimal_th(self.free_volume)
                self.connect([self.goal], self.th)
        if self.state == "PLANNING":
            super().update(1.1*self.th, max_milestones)

    def draw(self) -> None:
        if self.state == "PLANNING":
            return super().draw()
        if self.state == "VOLUME":
            GLUtils.draw_points(
                self.free_volume_sampler.free_pts,
                color = (0.85, 0.85, 0.85, 1.0)
            )
            GLUtils.draw_points(
                self.free_volume_sampler.non_free_pts,
                color = (0.1, 0.1, 0.7, 1.0)
            )

    def finished(self) -> bool:
        return len(self.milestones) >= self.n_samples

    def get_optimal_th(self, free_volume: float, d: int = 2) -> float:
        n = self.n_samples
        gamma = 2 * ((1 + 1/d) * free_volume/np.pi)**(1/d)
        optimal_th = gamma * (np.log(n)/n)**(1/d)
        return optimal_th
