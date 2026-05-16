from typing import Set, List, Tuple
from partition import RectangularPartition, Point
import time


class DPSolver:
    """Programação Dinâmica com bitmasks para vigilância de partições."""

    def __init__(self, partition: RectangularPartition, target_rectangles: Set[int] = None):
        self.partition = partition
        self.target_rectangles = target_rectangles or set(r.id for r in partition.rectangles)

        # Cobertura de cada vértice
        self.vertex_coverage = {}
        for v in partition.vertices:
            covered = partition.get_rectangles_covered_by_vertex(v) & self.target_rectangles
            if covered:
                self.vertex_coverage[v] = covered


    def solve(self, verbose: bool = False) -> Tuple[List[Point], int, float]:
        """DP com bitmasks: dp[mask] = (min_guardas, lista_guardas)"""

        start = time.time()

        # Mapear retângulos para bits
        rect_list = sorted(list(self.target_rectangles))
        rect_to_bit = {r: i for i, r in enumerate(rect_list)}
        full_mask = (1 << len(rect_list)) - 1

        # dp[mask] = (num_guardas, lista_guardas)
        dp = {0: (0, [])}

        for mask in range(1, full_mask + 1):
            dp[mask] = (float('inf'), [])

            for vertex, covered_rects in self.vertex_coverage.items():
                covered_mask = sum(1 << rect_to_bit[r] for r in covered_rects if r in rect_to_bit)

                if mask & covered_mask:
                    prev_mask = mask & ~covered_mask
                    if prev_mask in dp and dp[prev_mask][0] != float('inf'):
                        new_guards = dp[prev_mask][0] + 1
                        if new_guards < dp[mask][0]:
                            dp[mask] = (new_guards, dp[prev_mask][1] + [vertex])

        elapsed = time.time() - start

        # Solução
        num, guards = dp[full_mask]

        if verbose:
            result = f"{num} guardas" if num != float('inf') else "INF (sem solução)"
            print(f"DP: {result} em {elapsed:.4f}s")

        return guards, int(num) if num != float('inf') else 0, elapsed
