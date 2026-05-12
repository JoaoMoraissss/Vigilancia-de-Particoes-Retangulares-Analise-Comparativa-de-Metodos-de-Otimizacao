"""
Programação Inteira para Vigilância de Partições Retangulares
Usando Google OR-Tools (solver SCIP)

Tarefa 2: Programação Inteira e por Restrições
"""

from typing import Set, List, Tuple
from partition import RectangularPartition, Point
import time

try:
    from ortools.linear_solver import pywraplp
    ORTOOLS_AVAILABLE = True
except ImportError:
    ORTOOLS_AVAILABLE = False


class IntegerProgrammingSolver:
    
    def __init__(self, partition: RectangularPartition, 
                 target_rectangles: Set[int] = None):
        self.partition = partition
        
        if target_rectangles is None:
            self.target_rectangles = set(r.id for r in partition.rectangles)
        else:
            self.target_rectangles = target_rectangles
    
    
    def solve_with_ortools(self, time_limit: float = 300.0) -> Tuple[List[Point], int, float, str]:
  
        if not ORTOOLS_AVAILABLE:
            return [], 0, 0.0, "OR-Tools não disponível"
        
        start_time = time.time()
        
        #CRIAR SOLVER 
        solver = pywraplp.Solver.CreateSolver('SCIP')
        if not solver:
            return [], 0, 0.0, "Solver não criado"
        
        solver.SetTimeLimit(int(time_limit * 1000))
        
        #CRIAR VARIÁVEIS
        vertices_list = list(self.partition.vertices)
        x = {}
        
        for v in vertices_list:
            x[v] = solver.BoolVar(f'x_{v.x}_{v.y}')
        
        # FUNÇÃO OBJETIVO
        objective = solver.Objective()
        for v in vertices_list:
            objective.SetCoefficient(x[v], 1)
        objective.SetMinimization()
        
        print(f"Objetivo: minimizar número de guardas")
        
        # RESTRIÇÕES
 
        num_constraints = 0
        for rect_id in self.target_rectangles:
            # Vértices deste retângulo
            rect_vertices = self.partition.get_vertices_of_rectangle(rect_id)
            
            # Criar restrição: soma ≥ 1
            constraint = solver.Constraint(1, solver.infinity())
            
            for v in rect_vertices:
                if v in x:
                    constraint.SetCoefficient(x[v], 1)
            
            num_constraints += 1
        
        #RESOLVER 
        print(f"  🔧 Resolvendo...")
        
        status = solver.Solve()
        elapsed = time.time() - start_time
        
        # EXTRAIR SOLUÇÃO
        guards = []
        num_guards = 0
        
        if status == pywraplp.Solver.OPTIMAL:
            status_str = "OPTIMAL"
            print(f"Solução ÓTIMA encontrada!")
        elif status == pywraplp.Solver.FEASIBLE:
            status_str = "FEASIBLE"
            print(f"Solução viável encontrada (pode não ser ótima)")
        elif status == pywraplp.Solver.INFEASIBLE:
            status_str = "INFEASIBLE"
            print(f"Problema impossível de resolver")
            return [], 0, elapsed, status_str
        else:
            status_str = "UNKNOWN"
            print(f" Desconhecido")
            return [], 0, elapsed, status_str
        
        # Extrair guardas da solução
        for v in vertices_list:
            if x[v].solution_value() > 0.5:
                guards.append(v)
                num_guards += 1
        
        print(f"Guardas: {num_guards}")
        print(f"Tempo: {elapsed:.4f}s")
        
        return guards, num_guards, elapsed, status_str
    
    
    def print_model_info(self):
        """Imprime informações sobre o modelo"""
        
        print("\n" + "="*70)
        print("  MODELO DE PROGRAMAÇÃO INTEIRA")
        print("="*70)
        
        print("\n Variáveis de Decisão:")
        print(f"  x_v ∈ {{0,1}} para cada vértice v")
        print(f"  x_v = 1 se guarda colocado em v, 0 caso contrário")
        print(f"\n  Total: {len(self.partition.vertices)} variáveis")
        
        print("\n Função Objetivo:")
        print(f"  minimizar Σ_v x_v")
        print(f"  (minimizar número total de guardas)")
        
        print("\nRestrições:")
        print(f"  Para cada retângulo r:")
        print(f"  Σ_{{v ∈ V(r)}} x_v ≥ 1")
        print(f"  (pelo menos um guarda em algum vértice de r)")
        print(f"\n  Total: {len(self.target_rectangles)} restrições")
        
        print("="*70 + "\n")


# ==============================================================================
# TESTE
# ==============================================================================

if __name__ == "__main__":
    from partition import parse_partition_file
    
    # Carregar dados
    partitions = parse_partition_file("../data/step50")
    partition = partitions[0]
    
    print(f"\n{'='*70}")
    print(f"  TESTE: Programação Inteira com OR-Tools")
    print(f"{'='*70}\n")
    
    print(f"Partição: {len(partition.rectangles)} retângulos, "
          f"{len(partition.vertices)} vértices\n")
    
    # Criar solver
    solver = IntegerProgrammingSolver(partition)
    
    # Mostrar modelo
    solver.print_model_info()
    
    # Resolver
    guards, num_guards, elapsed, status = solver.solve_with_ortools(time_limit=60.0)
    
    print(f"\n{'='*70}")
    print(f"  RESULTADO")
    print(f"{'='*70}")
    print(f"  Status: {status}")
    print(f"  Guardas: {num_guards}")
    print(f"  Tempo: {elapsed:.4f}s")
    
    if num_guards > 0 and num_guards <= 10:
        print(f"\n  Posições dos guardas:")
        for i, g in enumerate(guards, 1):
            print(f"    {i}. {g}")
    
    print(f"{'='*70}\n")