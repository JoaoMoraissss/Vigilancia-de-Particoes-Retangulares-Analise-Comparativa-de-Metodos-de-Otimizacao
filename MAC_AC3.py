from typing import Set, List, Tuple, Dict
from partition import RectangularPartition, Point
import time
from collections import deque


class CSPSolver:
    
    def __init__(self, partition: RectangularPartition, 
                 target_rectangles: Set[int] = None):
        self.partition = partition
        
        if target_rectangles is None:
            self.target_rectangles = set(r.id for r in partition.rectangles)
        else:
            self.target_rectangles = target_rectangles

        self.variables = list(self.partition.vertices)
        
        self.initial_domains = {v: {0, 1} for v in self.variables}
        
        # Restrições: cada retângulo deve ter pelo menos um guarda
        self.constraints = []
        for rect_id in self.target_rectangles:
            rect_vertices = list(self.partition.get_vertices_of_rectangle(rect_id))
            self.constraints.append({
                'type': 'at_least_one',
                'vertices': rect_vertices,
                'rect_id': rect_id
            })
        
        # Estatísticas
        self.nodes_explored = 0
        self.backtracks = 0
        self.ac3_calls = 0
    
    

    # AC-3: Arc Consistency Algorithm 3
    
    def ac3(self, domains: Dict[Point, Set[int]]) -> bool:
        """
        Algoritmo AC-3 para propagação de restrições.
        
        Ideia:
        ------
        Para cada par de variáveis relacionadas (arco), 
        remover valores inconsistentes dos domínios.
        
        Retorna:
        --------
        True se consistente (nenhum domínio ficou vazio)
        False se inconsistente (algum domínio ficou vazio)
        """
        self.ac3_calls += 1
        
        # Criar fila de arcos (pares de variáveis relacionadas)
        queue = deque()
        
        # Para cada restrição, adicionar todos os pares
        for constraint in self.constraints:
            vertices = constraint['vertices']
            # Cada par de vértices da mesma restrição forma um arco
            for i, v1 in enumerate(vertices):
                for v2 in vertices[i+1:]:
                    queue.append((v1, v2, constraint))
                    queue.append((v2, v1, constraint))
        
        # Processar fila
        while queue:
            v1, v2, constraint = queue.popleft()
            
            # Tentar revisar domínio de v1 em relação a v2
            if self.revise(domains, v1, v2, constraint):
                # Domínio de v1 foi modificado
                
                # Verificar se ficou vazio (inconsistência!)
                if not domains[v1]:
                    return False
                
                # Adicionar arcos vizinhos à fila (propagação)
                for c in self.constraints:
                    if v1 in c['vertices']:
                        for v in c['vertices']:
                            if v != v1 and v != v2:
                                queue.append((v, v1, c))
        
        return True
    
    
    def revise(self, domains: Dict[Point, Set[int]], 
               v1: Point, v2: Point, constraint: dict) -> bool:
        """
        Revisa domínio de v1 em relação a v2 dada a restrição.
        
        Remove valores de v1 que não têm suporte em v2.
        
        Retorna:
        --------
        True se domínio de v1 foi modificado
        False caso contrário
        """
        revised = False
        
        if constraint['type'] == 'at_least_one':
            # Restrição: pelo menos um vértice = 1
            
            vertices = constraint['vertices']
            other_vertices = [v for v in vertices if v != v1]
            
            # Verificar se 0 é viável para v1
            if 0 in domains[v1]:
                # 0 só é viável se outro vértice pode ser 1
                can_be_zero = any(1 in domains[v] for v in other_vertices)
                
                if not can_be_zero:
                    # Nenhum outro pode ser 1, então v1 DEVE ser 1
                    domains[v1].discard(0)
                    revised = True
            
            # Verificar se 1 é viável para v1
            # (sempre é, desde que domínio não esteja vazio)
        
        return revised
    
    
    # FORWARD CHECKING
    
    def forward_checking(self, assignment: Dict[Point, int],
                        domains: Dict[Point, Set[int]]) -> Dict[Point, Set[int]]:
        """
        Forward checking: propagar atribuição atual.
        
        Quando atribuímos x_v = val, atualizar domínios das outras variáveis.
        """
        new_domains = {v: d.copy() for v, d in domains.items()}
        
        # Para cada restrição
        for constraint in self.constraints:
            if constraint['type'] == 'at_least_one':
                vertices = constraint['vertices']
                
                # Contar guardas já atribuídos
                assigned_to_one = sum(1 for v in vertices 
                                     if v in assignment and assignment[v] == 1)
                
                unassigned = [v for v in vertices if v not in assignment]
                
                if assigned_to_one > 0:
                    # Restrição já satisfeita!
                    # Outros vértices podem ser 0 ou 1
                    pass
                
                elif len(unassigned) == 1:
                    # Última variável não atribuída DEVE ser 1
                    v = unassigned[0]
                    if v in new_domains:
                        new_domains[v] = {1}
                
                elif len(unassigned) == 0:
                    # Todos atribuídos mas nenhum = 1
                    # Inconsistência! (mas já foi detectada antes)
                    pass
        
        return new_domains
    
    
    # HEURÍSTICAS
    
    def select_variable_mrv(self, assignment: Dict[Point, int],
                           domains: Dict[Point, Set[int]]) -> Point:
        """
        Heurística MRV: Minimum Remaining Values
        
        Escolhe variável com MENOR domínio (mais restrita).
        Quebra empates por grau (mais restrições).
        """
        unassigned = [v for v in self.variables if v not in assignment]
        
        if not unassigned:
            return None
        
        # MRV: menor domínio
        min_domain_size = min(len(domains[v]) for v in unassigned)
        candidates = [v for v in unassigned if len(domains[v]) == min_domain_size]
        
        if len(candidates) == 1:
            return candidates[0]
        
        # Desempate: grau (número de restrições em que aparece)
        def degree(v):
            return sum(1 for c in self.constraints if v in c['vertices'])
        
        return max(candidates, key=degree)
    
    
    def order_domain_values_lcv(self, variable: Point, 
                                assignment: Dict[Point, int],
                                domains: Dict[Point, Set[int]]) -> List[int]:
        """
        Heurística LCV: Least Constraining Value
        
        Ordena valores do domínio por "menos restritivos".
        Para minimização: preferir 0 (não colocar guarda).
        """
        # Para minimização, preferir 0
        domain_list = list(domains[variable])
        
        if 0 in domain_list and 1 in domain_list:
            return [0, 1]  # Tentar 0 primeiro
        else:
            return domain_list
    
    
    
    # BACKTRACKING COM MAC
    
    def backtracking_search(self, assignment: Dict[Point, int],
                           domains: Dict[Point, Set[int]],
                           best_solution: dict) -> bool:
        """
        Backtracking com MAC (Maintaining Arc Consistency).
        
        Em cada nó:
        1. Selecionar variável (MRV)
        2. Para cada valor (LCV):
           a. Atribuir
           b. Forward checking
           c. AC-3
           d. Se consistente, recursão
           e. Desfazer atribuição
        """
        self.nodes_explored += 1
        
        # Imprimir progresso a cada 1000 nós
        if self.nodes_explored % 1000 == 0:
            current_guards = sum(assignment.values())
            best = best_solution['count'] if best_solution['count'] else '?'
            print(f"    Nós: {self.nodes_explored}, "
                  f"Guardas atuais: {current_guards}, "
                  f"Melhor: {best}")
        
        # ===== CASO BASE: Solução completa =====
        if len(assignment) == len(self.variables):
            num_guards = sum(assignment.values())
            
            # Atualizar melhor solução
            if best_solution['count'] is None or num_guards < best_solution['count']:
                best_solution['assignment'] = assignment.copy()
                best_solution['count'] = num_guards
                print(f"Nova melhor solução: {num_guards} guardas "
                      f"(nós: {self.nodes_explored})")
            
            return True
        
        # ===== PODA: Se já pior que melhor solução =====
        current_guards = sum(assignment.values())
        if best_solution['count'] is not None:
            if current_guards >= best_solution['count']:
                return False
        
        # ===== SELECIONAR VARIÁVEL (MRV) =====
        var = self.select_variable_mrv(assignment, domains)
        if var is None:
            return False
        
        # ===== TENTAR VALORES (LCV) =====
        for value in self.order_domain_values_lcv(var, assignment, domains):
            # Atribuir
            assignment[var] = value
            
            # Forward checking
            new_domains = self.forward_checking(assignment, domains)
            
            # Verificar se algum domínio ficou vazio
            all_nonempty = all(len(new_domains[v]) > 0 
                              for v in self.variables 
                              if v not in assignment)
            
            if all_nonempty:
                # AC-3: propagar restrições
                if self.ac3(new_domains):
                    # Consistente! Recursão
                    self.backtracking_search(assignment, new_domains, best_solution)
                else:
                    # AC-3 detectou inconsistência
                    self.backtracks += 1
            else:
                # Forward checking detectou inconsistência
                self.backtracks += 1
            
            # Desfazer atribuição
            del assignment[var]
        
        return False
    
    
    # =========================================================================
    # SOLVER PRINCIPAL
    # =========================================================================
    
    def solve(self, time_limit: float = 300.0) -> Tuple[List[Point], int, float, str]:
        """
        Resolve o CSP usando MAC + AC-3.
        
        Returns:
        --------
        (lista_guardas, número_guardas, tempo, status)
        """
        start_time = time.time()
        
        print("\n" + "="*70)
        print("  CSP SOLVER: MAC + AC-3")
        print("="*70)
        print(f"\nProblema:")
        print(f"  Variáveis: {len(self.variables)}")
        print(f"  Restrições: {len(self.constraints)}")
        print(f"  Domínio inicial: {{0, 1}} para cada variável")
        
        print("\nFase 1: Propagação inicial (AC-3)...")
        
        # AC-3 inicial
        initial_domains = {v: d.copy() for v, d in self.initial_domains.items()}
        
        if not self.ac3(initial_domains):
            elapsed = time.time() - start_time
            print("Inconsistência detectada na propagação inicial!")
            return [], 0, elapsed, "INFEASIBLE"
        
        # Contar domínios reduzidos
        reduced = sum(1 for v in self.variables if len(initial_domains[v]) < 2)
        print(f"  Propagação completa")
        print(f" Domínios reduzidos: {reduced}/{len(self.variables)}")
        
        print("\nFase 2: Busca com backtracking + MAC...")
        
        # Backtracking search
        best_solution = {'assignment': None, 'count': None}
        assignment = {}
        
        self.backtracking_search(assignment, initial_domains, best_solution)
        
        elapsed = time.time() - start_time
        
        # ===== RESULTADO =====
        
        print("\n" + "="*70)
        print("  ESTATÍSTICAS")
        print("="*70)
        print(f"  Nós explorados: {self.nodes_explored:,}")
        print(f"  Backtracks: {self.backtracks:,}")
        print(f"  Chamadas AC-3: {self.ac3_calls:,}")
        print(f"  Tempo: {elapsed:.4f}s")
        
        # Verificar timeout
        if elapsed >= time_limit:
            status = "TIMEOUT"
        elif best_solution['assignment'] is None:
            status = "INFEASIBLE"
        else:
            status = "FEASIBLE"
        
        # Extrair guardas
        guards = []
        num_guards = 0
        
        if best_solution['assignment']:
            for v, val in best_solution['assignment'].items():
                if val == 1:
                    guards.append(v)
                    num_guards += 1
        
        print("\n" + "="*70)
        print("  RESULTADO")
        print("="*70)
        print(f"  Status: {status}")
        print(f"  Guardas: {num_guards}")
        print(f"  Tempo: {elapsed:.4f}s")
        print("="*70 + "\n")
        
        return guards, num_guards, elapsed, status


# =============================================================================
# TESTE
# =============================================================================

if __name__ == "__main__":
    from partition import parse_partition_file
    
    print("\n" + "="*70)
    print("  TESTE: CSP com MAC + AC-3")
    print("="*70 + "\n")
    
    # Carregar dados
    partitions = parse_partition_file("../data/step50")
    
    # AVISO: MAC é lento! Testar só instâncias pequenas
    for i, partition in enumerate(partitions[:1]):
        
        # Filtrar para instância pequena (primeiros N retângulos)
        if len(partition.rectangles) > 10:
            print(f"Instância {i} muito grande ({len(partition.rectangles)} retângulos)")
            print(f"   Reduzindo para 8 retângulos para teste...\n")
            
            # Pegar só primeiros 8 retângulos
            small_rects = partition.rectangles[:8]
            small_partition = type(partition)(small_rects)
            partition = small_partition
        
        print(f"Instância {i}:")
        print(f"   Retângulos: {len(partition.rectangles)}")
        print(f"   Vértices: {len(partition.vertices)}\n")
        
        # Resolver
        solver = CSPSolver(partition)
        guards, num_guards, elapsed, status = solver.solve(time_limit=120.0)
        
        if num_guards > 0 and num_guards <= 10:
            print(f"\nPosições dos guardas:")
            for idx, g in enumerate(guards, 1):
                print(f"   {idx}. {g}")