import numpy as np
from scipy.sparse import csr_array
from scipy.sparse.csgraph import dijkstra

from scene.scenes import Point
from shapes import Segment, Path, Circle
import collisions


class IndexedSegment(Segment):
    def __init__(
            self,
            point_i: Point,
            point_j: Point,
            pi_idx: int,
            pj_idx: int
    ) -> None:
        super().__init__(point_i, point_j)
        self.pi_idx = pi_idx
        self.pj_idx = pj_idx


class ProbabilisticRandomMap:
    def __init__(
            self,
            polygons: list,
            radius: float,
            start: Point,
            goal: Point,
        ) -> None:
        self.polygons = polygons
        self.radius = radius
        self.th = 0.5
        self.reset(start, goal)

    def reset(self, start: Point = None, goal: Point = None) -> None:
        if start is None:
            start = self.start
        if goal is None:
            goal = self.goal()
        self.start = start
        self.goal = goal
        self.milestones = [self.start, self.goal]
        self.edges = []
        self.connect([self.goal], self.th)
        self.path_exists = False
        self.cost = np.inf
        self.last_cost = np.inf
        self.shortest_path = self.get_shortest_path()

    def sample_free_points(self, n: int = 1) -> list:
        samples = []
        n_samples = 0
        while True:
            array = np.random.uniform(-1, 1, 2)
            sample = Point(array[0], array[1])
            if not collisions.point_collides(sample, self.polygons, self.radius):
                n_samples += 1
                samples.append(sample)
                if n == n_samples:
                    return samples

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

    def connect(self, new_milestones: list, th: float, max_nn: int = 20) -> None:
        new_edges = []
        last_processed_idx = len(self.milestones) - len(new_milestones)
        for vi, v in enumerate(new_milestones):
            all_segments = (
                IndexedSegment(u, v, ui, last_processed_idx+vi)
                for ui, u in enumerate(self.milestones)
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

    def update(self, th: float = None, max_milestones: int = 200) -> bool:
        not_finished = True
        if self.path_exists or len(self.milestones) > max_milestones + 1:
            not_finished = False
        new_milestones = self.sample(1)
        if th is None:
            th = self.th
        self.connect(new_milestones, th)
        self.shortest_path = self.get_shortest_path()

        return not_finished

    def get_matrix(self) -> np.ndarray:
        n = len(self.milestones)
        matrix = -np.ones((n, n))
        for indexed_edge in self.edges:
            distance = indexed_edge.len()
            matrix[indexed_edge.pi_idx, indexed_edge.pj_idx] = distance
            matrix[indexed_edge.pj_idx, indexed_edge.pi_idx] = distance
        return matrix

    def get_shortest_path(self) -> object:
        matrix = self.get_matrix()
        graph = csr_array(matrix)
        graph[graph < 0] = np.inf

        i = 0
        j = 1

        dist_matrix, predecessors = dijkstra(
            csgraph=graph,
            directed=False,
            indices = i,
            return_predecessors=True
        )

        self.last_cost = self.cost
        self.cost = dist_matrix[j]
        if dist_matrix[j] == np.inf:
            return

        self.path_exists = True
        path = []

        current = j
        while current != i:
            path.append(current)
            current = predecessors[current]
        path.append(current)

        vertices_path = [self.milestones[vertex_i] for vertex_i in path]

        return Path(vertices_path)

    def draw(self) -> None:
        for segment in self.edges:
            segment.draw(color = (1.0, 0.8, 0.5, 1.0))
        if self.shortest_path:
            self.shortest_path.draw(color = (1.0, 0, 0, 1.0))
        for milestone in self.milestones:
            vertex = Circle(milestone, 0.015)
            vertex.draw(color = (220/255, 88/255, 88/255, 1.0))

    def finished(self) -> bool:
        return self.cost != np.inf
