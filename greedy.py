from typing import Set, List, Tuple
from partition import RectangularPartition, Point
import time


class GreedySolver:
    """
    Implementa 4 estratégias greedy para o problema.
    
    Todas têm a mesma estrutura:
    1. Loop enquanto há retângulos não cobertos
    2. Escolher "melhor" vértice (critério diferente)
    3. Colocar guarda
    4. Atualizar retângulos cobertos
    """
    
    def __init__(self, partition: RectangularPartition, 
                 target_rectangles: Set[int] = None):
        self.partition = partition
        
        # Se não especificar, cobrir TODOS os retângulos
        if target_rectangles is None:
            self.target_rectangles = set(r.id for r in partition.rectangles)
        else:
            self.target_rectangles = target_rectangles
    
    
# ESTRATÉGIA 1: MAX COVERAGE
    """
        Escolhe sempre o vértice que cobre MAIS retângulos não cobertos.
        
        Critério: max |cobertos_pelo_vértice ∩ não_cobertos|
        
        Returns:
            (lista_de_guardas, número_guardas, tempo_execução)
    """
  
    
    def max_coverage_greedy(self) -> Tuple[List[Point], int, float]:

        start_time = time.time()
        
        guards = []
        uncovered = self.target_rectangles.copy()
        
        while uncovered: 
            best_vertex = None
            best_coverage = 0
            
            # Procurar vértice que cobre mais retângulos não cobertos
            for vertex in self.partition.vertices:
                covered_by_vertex = self.partition.get_rectangles_covered_by_vertex(vertex)
                
                new_coverage = len(covered_by_vertex & uncovered)
                
                if new_coverage > best_coverage:
                    best_coverage = new_coverage
                    best_vertex = vertex
            
            if best_vertex is None:
                break  
            
          
            guards.append(best_vertex)
            
            covered_by_vertex = self.partition.get_rectangles_covered_by_vertex(best_vertex)
            uncovered -= covered_by_vertex
        
        elapsed = time.time() - start_time
        return guards, len(guards), elapsed
    

    # ESTRATÉGIA 2: MIN DEGREE
    """
        Prioriza retângulos com MENOS vértices (mais difíceis de cobrir).
        
        Lógica:
        1. Encontrar retângulo não coberto com menos vértices
        2. Dentre os vértices desse retângulo, escolher o que cobre mais
        
        Critério: ataca os retângulos "difíceis" primeiro
    """
        
    def min_degree_greedy(self) -> Tuple[List[Point], int, float]:

        start_time = time.time()
        
        guards = []
        uncovered = self.target_rectangles.copy()
        
        while uncovered:
            #Achar retângulo mais difícil 
            min_rect = None
            min_vertices = float('inf')
            
            for rect_id in uncovered:
                vertices = self.partition.get_vertices_of_rectangle(rect_id)
                if len(vertices) < min_vertices:
                    min_vertices = len(vertices)
                    min_rect = rect_id
            
            if min_rect is None:
                break
            
            #Escolher melhor vértice DESTE retângulo
            best_vertex = None
            best_coverage = 0
            
            rect_vertices = self.partition.get_vertices_of_rectangle(min_rect)
            for vertex in rect_vertices:
                covered_by_vertex = self.partition.get_rectangles_covered_by_vertex(vertex)
                new_coverage = len(covered_by_vertex & uncovered)
                
                if new_coverage > best_coverage:
                    best_coverage = new_coverage
                    best_vertex = vertex
            
            if best_vertex:
                guards.append(best_vertex)
                covered_by_vertex = self.partition.get_rectangles_covered_by_vertex(best_vertex)
                uncovered -= covered_by_vertex
        
        elapsed = time.time() - start_time
        return guards, len(guards), elapsed
    
    
    # ESTRATÉGIA 3: FREQUENCY WEIGHTED
    """
        Considera tanto COBERTURA quanto RARIDADE do vértice.
        
        Score = cobertura × (1 + 1/frequência)
        
        Lógica: vértices que aparecem em POUCOS retângulos são "críticos"
    """ 
    def frequency_weighted_greedy(self) -> Tuple[List[Point], int, float]:

        start_time = time.time()
        
        guards = []
        uncovered = self.target_rectangles.copy()
        
        while uncovered:
            best_vertex = None
            best_score = -1
            
            for vertex in self.partition.vertices:
                covered_by_vertex = self.partition.get_rectangles_covered_by_vertex(vertex)
                new_coverage = covered_by_vertex & uncovered
                
                if not new_coverage:
                    continue
                
                frequency = len(covered_by_vertex)  # Total de retângulos
                score = len(new_coverage) * (1.0 + 1.0/frequency)
                
                if score > best_score:
                    best_score = score
                    best_vertex = vertex
            
            if best_vertex is None:
                break
            
            guards.append(best_vertex)
            covered_by_vertex = self.partition.get_rectangles_covered_by_vertex(best_vertex)
            uncovered -= covered_by_vertex
        
        elapsed = time.time() - start_time
        return guards, len(guards), elapsed
    
    
    # ESTRATÉGIA 4: RANDOM GREEDY (com aleatoriedade)
    """
        Greedy com aleatoriedade para escapar de mínimos locais.
        
        Com probabilidade `randomness`, escolhe aleatoriamente 
        entre os top 30% candidatos.
    """

    def random_greedy(self, randomness: float = 0.3) -> Tuple[List[Point], int, float]:
        import random
        start_time = time.time()
        
        guards = []
        uncovered = self.target_rectangles.copy()
        
        while uncovered:
            candidates = []
            
            # Calcular cobertura de todos os vértices
            for vertex in self.partition.vertices:
                covered_by_vertex = self.partition.get_rectangles_covered_by_vertex(vertex)
                new_coverage = len(covered_by_vertex & uncovered)
                
                if new_coverage > 0:
                    candidates.append((vertex, new_coverage))
            
            if not candidates:
                break
            
            # Ordenar por cobertura (melhor primeiro)
            candidates.sort(key=lambda x: x[1], reverse=True)
            
            # Escolher: melhor OU aleatório entre top 30%
            if random.random() < randomness and len(candidates) > 1:
                top_n = max(1, int(len(candidates) * 0.3))
                chosen_vertex = random.choice(candidates[:top_n])[0]
            else:
                chosen_vertex = candidates[0][0]
            
            guards.append(chosen_vertex)
            covered_by_vertex = self.partition.get_rectangles_covered_by_vertex(chosen_vertex)
            uncovered -= covered_by_vertex
        
        elapsed = time.time() - start_time
        return guards, len(guards), elapsed
    
    
    # FUNÇÃO PARA COMPARAR TODAS
    def compare_strategies(self) -> dict:
        
        print("Testar estratégias greedy...")
        results = {}
        
        # 1 Max Coverage
        guards1, n1, t1 = self.max_coverage_greedy()
        results['max_coverage'] = {'guards': guards1, 'count': n1, 'time': t1}
        print(f"  Max Coverage: {n1} guardas em {t1:.4f}s")
        
        # 2 Min Degree
        guards2, n2, t2 = self.min_degree_greedy()
        results['min_degree'] = {'guards': guards2, 'count': n2, 'time': t2}
        print(f"  Min Degree: {n2} guardas em {t2:.4f}s")
        
        # 3 Frequency Weighted
        guards3, n3, t3 = self.frequency_weighted_greedy()
        results['frequency_weighted'] = {'guards': guards3, 'count': n3, 'time': t3}
        print(f"  Frequency Weighted: {n3} guardas em {t3:.4f}s")
        
        # 4 Random Greedy (média de 10 execuções)
        counts = []
        times = []
        for _ in range(10):
            _, n4, t4 = self.random_greedy()
            counts.append(n4)
            times.append(t4)
        
        avg_count = sum(counts) / len(counts)
        avg_time = sum(times) / len(times)
        results['random_greedy'] = {
            'count': avg_count,
            'time': avg_time,
            'min': min(counts),
            'max': max(counts)
        }
        print(f"  Random Greedy: {avg_count:.1f} guardas (min={min(counts)}, max={max(counts)})")
        
        best = min([n1, n2, n3, min(counts)])
        print(f"\n✅ Melhor: {best} guardas")
        
        return results

