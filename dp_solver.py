from typing import Set, List, Tuple
from partition import RectangularPartition, Point
import time


class DPSolver:
    """
    Programação Dinâmica para o problema de vigilância.
    
    ABORDAGEM 1: DP sobre subconjuntos (exato, mas exponencial)
    - Viável para n ≤ 20 retângulos
    - Garante solução ÓTIMA
    
    ABORDAGEM 2: DP Greedy (híbrido)
    - Para instâncias maiores
    - Não garante ótimo
    """
    
    def __init__(self, partition: RectangularPartition):
        self.partition = partition
        self.target_rectangles = set(r.id for r in partition.rectangles)
        self.vertex_coverage = {}
        for v in self.partition.vertices:
            covered = self.partition.get_rectangles_covered_by_vertex(v)
            covered = covered & self.target_rectangles
            if covered:
                self.vertex_coverage[v] = covered
    

    #  DP EXATO (sobre subconjuntos)
    
    def solve_exact_dp(self) -> Tuple[List[Point], int, float, str]:
        """
        DP exato usando bitmasks para representar subconjuntos.
        
        Estado: dp[mask] = (min_guardas, lista_guardas)
        onde mask é um subconjunto dos retângulos a cobrir
        
        Complexidade: O(2^n × m) onde n=retângulos, m=vértices
        """
        n_rects = len(self.target_rectangles)
        
        # Só viável para n pequeno
        if n_rects > 20:
            return [], 0, 0.0, "TOO_LARGE"
        
        start_time = time.time()
        
        # Mapear retângulos para bits
        rect_list = sorted(list(self.target_rectangles))
        rect_to_bit = {r: i for i, r in enumerate(rect_list)}
        
        full_mask = (1 << n_rects) - 1  # Todos os retângulos
        
        # dp[mask] = (num_guardas, lista_guardas)
        dp = {}
        dp[0] = (0, [])  # Nenhum retângulo = 0 guardas
        
        # Para cada subconjunto (em ordem crescente)
        for mask in range(1, full_mask + 1):
            dp[mask] = (float('inf'), [])
            
            # Tentar cada vértice
            for vertex, covered_rects in self.vertex_coverage.items():
                # Converter retângulos cobertos para bitmask
                covered_mask = 0
                for r in covered_rects:
                    if r in rect_to_bit:
                        covered_mask |= (1 << rect_to_bit[r])
                
                # Se este vértice cobre algum retângulo em mask
                if mask & covered_mask:
                    # Estado anterior: remover retângulos cobertos
                    prev_mask = mask & ~covered_mask
                    
                    if prev_mask in dp:
                        prev_guards, prev_list = dp[prev_mask]
                        new_guards = prev_guards + 1
                        
                        # Se melhor que atual
                        if new_guards < dp[mask][0]:
                            dp[mask] = (new_guards, prev_list + [vertex])
        
        elapsed = time.time() - start_time
        
        # Solução final
        if full_mask in dp:
            num_guards, guards = dp[full_mask]
            if num_guards < float('inf'):
                return guards, num_guards, elapsed, "OPTIMAL"
        
        return [], 0, elapsed, "INFEASIBLE"
    
    
    # DP GREEDY 
    def solve_greedy_dp(self) -> Tuple[List[Point], int, float, str]:
        """
        Híbrido: Greedy até sobrar poucos retângulos, depois DP exato.
        
        Estratégia:
        1. Usar greedy enquanto n_uncovered > 15
        2. Quando sobram ≤ 15, usar DP exato
        """
        start_time = time.time()
        
        print(f"DP Greedy Híbrido")
        
        guards = []
        uncovered = self.target_rectangles.copy()
        
        #Greedy
        while len(uncovered) > 15:
            best_vertex = None
            best_coverage = set()
            
            for vertex, covered_rects in self.vertex_coverage.items():
                if vertex in guards:
                    continue
                
                new_coverage = covered_rects & uncovered
                if len(new_coverage) > len(best_coverage):
                    best_coverage = new_coverage
                    best_vertex = vertex
            
            if not best_vertex:
                break
            
            guards.append(best_vertex)
            uncovered -= best_coverage
        
        # DP
        if uncovered:
            print(f"    Mudando para DP exato com {len(uncovered)} retângulos...")
            
            sub_solver = DPSolver(self.partition)
            sub_solver.target_rectangles = uncovered
            
            # Recalcular cobertura
            sub_solver.vertex_coverage = {}
            for v in self.partition.vertices:
                covered = self.partition.get_rectangles_covered_by_vertex(v)
                covered = covered & uncovered
                if covered:
                    sub_solver.vertex_coverage[v] = covered
            
            # Resolver
            remaining_guards, n_remaining, _, status = sub_solver.solve_exact_dp()
            
            if status == "OPTIMAL":
                guards.extend(remaining_guards)
        
        elapsed = time.time() - start_time
        
        return guards, len(guards), elapsed, "FEASIBLE"
    
    
    # =================================================================
    # MÉTODO 3: DP BOTTOM-UP (construção incremental)
    # =================================================================
    
    def solve_bottom_up_dp(self) -> Tuple[List[Point], int, float, str]:
        """
        DP construindo solução incrementalmente.
        
        Ordenar retângulos por dificuldade (menos vértices primeiro)
        e decidir melhor vértice considerando futuro.
        """
        start_time = time.time()
        
        # Ordenar retângulos por número de vértices (difíceis primeiro)
        rect_order = sorted(
            list(self.target_rectangles),
            key=lambda r: len(self.partition.get_vertices_of_rectangle(r))
        )
        
        guards = []
        covered = set()
        
        for rect_id in rect_order:
            # Se já coberto, skip
            if rect_id in covered:
                continue
            
            # Encontrar melhor vértice para este retângulo
            rect_vertices = self.partition.get_vertices_of_rectangle(rect_id)
            
            best_vertex = None
            best_extra_coverage = 0
            
            for v in rect_vertices:
                if v in guards:
                    continue
                
                # Quantos retângulos extras este vértice cobre?
                extra = len(self.vertex_coverage.get(v, set()) - covered)
                
                if extra > best_extra_coverage:
                    best_extra_coverage = extra
                    best_vertex = v
            
            if best_vertex:
                guards.append(best_vertex)
                covered.update(self.vertex_coverage.get(best_vertex, set()))
        
        elapsed = time.time() - start_time
        
        return guards, len(guards), elapsed, "FEASIBLE"


# =================================================================
# TESTE
# =================================================================

if __name__ == "__main__":
    from partition import parse_partition_file
    
    print("\n" + "="*70)
    print("  TESTE: Programação Dinâmica")
    print("="*70 + "\n")
    
    # Carregar dados
    partitions = parse_partition_file("../data/step50")
    
    for i, partition in enumerate(partitions[:2]):
        print(f"\n{'─'*70}")
        print(f"INSTÂNCIA {i}")
        print(f"  {len(partition.rectangles)} retângulos, {len(partition.vertices)} vértices")
        print(f"{'─'*70}\n")
        
        solver = DPSolver(partition)
        
        # Testar DP Exato (se viável)
        if len(partition.rectangles) <= 15:
            print("DP Exato:")
            guards, n, t, status = solver.solve_exact_dp()
            print(f"Guardas: {n}, Tempo: {t:.4f}s, Status: {status}\n")
        else:
            print("DP Exato: instância muito grande, pulando...\n")
        
        # DP Greedy
        print("DP Greedy (Híbrido):")
        guards, n, t, status = solver.solve_greedy_dp()
        print(f"Guardas: {n}, Tempo: {t:.4f}s, Status: {status}\n")
        
        # DP Bottom-up
        print("DP Bottom-up:")
        guards, n, t, status = solver.solve_bottom_up_dp()
        print(f"Guardas: {n}, Tempo: {t:.4f}s, Status: {status}\n")
    
    print("="*70 + "\n")