from typing import Set, List, Tuple, Dict
from partition import RectangularPartition, Point
import time
from collections import deque


class CSPSolver:

    def __init__(self, partition: RectangularPartition, target_rectangles: Set[int] = None):
        self.partition = partition
        self.target_rectangles = target_rectangles or set(r.id for r in partition.rectangles)
        self.variables = list(partition.vertices)

        # Cada retângulo deve ter pelo menos um guarda nos seus vértices
        self.constraints = [
            list(partition.get_vertices_of_rectangle(r)) for r in self.target_rectangles
        ]

        self.best_solution = None
        self.best_count = float('inf')

    #AC-3
    def ac3(self, domains: Dict[Point, Set[int]]) -> bool:
        queue = deque()

        # Criar arcos
        for constraint in self.constraints:
            for i, v1 in enumerate(constraint):
                for v2 in constraint[i+1:]:
                    queue.append((v1, v2, constraint))
                    queue.append((v2, v1, constraint))

        while queue:
            v1, v2, constraint = queue.popleft()

            # Verificar se é consistente
            if 0 in domains[v1]:
                others = [v for v in constraint if v != v1]
                if not any(1 in domains[v] for v in others):
                    domains[v1].discard(0)
                    if not domains[v1]:
                        return False

                    # Propagar mudança
                    for c in self.constraints:
                        if v1 in c:
                            for v in c:
                                if v != v1 and v != v2:
                                    queue.append((v, v1, c))
        return True

    #BACKTRACKING COM MAC
    def backtrack(self, assignment: Dict[Point, int], domains: Dict[Point, Set[int]]):

        if len(assignment) == len(self.variables):
            count = sum(assignment.values())
            if count < self.best_count:
                self.best_solution = assignment.copy()
                self.best_count = count
            return

        # Poda
        if sum(assignment.values()) >= self.best_count:
            return
        
        unassigned = [v for v in self.variables if v not in assignment]
        var = min(unassigned, key=lambda v: len(domains[v]))

        values = [0, 1] if 0 in domains[var] and 1 in domains[var] else list(domains[var])

        for value in values:
            assignment[var] = value
            new_domains = {v: d.copy() for v, d in domains.items()}

            # Forward checking que é se a restrição for satisfeita, propagar
            for constraint in self.constraints:
                assigned_ones = sum(1 for v in constraint if v in assignment and assignment[v] == 1)
                unassigned_c = [v for v in constraint if v not in assignment]

                if assigned_ones == 0 and len(unassigned_c) == 1:
                    new_domains[unassigned_c[0]] = {1}

            # Verificar domínios não vazios
            if all(len(new_domains[v]) > 0 for v in unassigned if v != var):
                # Chamar AC-3 após atribuição
                if self.ac3(new_domains):
                    self.backtrack(assignment, new_domains)

            del assignment[var]


    def solve(self, verbose: bool = False) -> Tuple[List[Point], int, float]:
        """Resolve usando MAC + AC-3"""
        start = time.time()

        # Domínios iniciais
        domains = {v: {0, 1} for v in self.variables}

        # AC-3 inicial
        if not self.ac3(domains):
            return [], 0, time.time() - start

        # Backtracking
        self.backtrack({}, domains)

        elapsed = time.time() - start

        # Extrair guardas
        guards = []
        if self.best_solution:
            guards = [v for v, val in self.best_solution.items() if val == 1]

        if verbose:
            print(f"MAC+AC3: {len(guards)} guardas em {elapsed:.4f}s")

        return guards, len(guards), elapsed
