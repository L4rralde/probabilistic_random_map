from copy import copy

import numpy as np

from scene.scenes import Point
from shapes import Segment
import collisions

class ProbabilisticRandomMap:
    def __init__(
            self,
            polygons: list,
            radius: float,
            start: Point,
            goal: Point,
        ) -> None:
        self.polygons = polygons
        self.milestones = [start, goal]
        self.radius = radius
        self.edges = []

    def sample(self, ntries: int = 5) -> list:
        milestones_candidates = [
            Point(*array)
            for array in np.random.uniform(-1, 1, (ntries, 2))
        ]
        new_milestones = [
            new_milestone
            for new_milestone in milestones_candidates
            if not collisions.point_collides(
                new_milestone,
                self.polygons,
                self.radius
            )
        ]
        self.milestones += new_milestones
        return new_milestones

    def connect(self, new_milestones: list, th: float, max_nn: int = 5) -> None:
        new_edges = []
        for v in new_milestones:
            all_segments = (
                Segment(u, v)
                for u in self.milestones
                if u != v
            )
            near_segments = (
                segment
                for segment in all_segments
                if segment.len() < th
            )
            near_segments = sorted(near_segments, key=lambda x: x.len())
            collision_free_segments = (
                segment
                for segment in near_segments[:max_nn]
                if not collisions.segment_collides(
                    segment,
                    self.polygons,
                    self.radius
                )
            )
            new_edges += list(collision_free_segments)
        self.edges += new_edges

    def update(self, th: float = 0.5, max_milestones: int = 200) -> bool:
        if len(self.milestones) > max_milestones + 1:
            return False
        new_milestones = self.sample(1)
        self.connect(new_milestones, th)
        return True
