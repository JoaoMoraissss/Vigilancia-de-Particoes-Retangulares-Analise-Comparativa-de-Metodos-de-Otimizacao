"""
Main - Vigilância de Partições Retangulares
MAD 2025/2026
"""

import json
from pathlib import Path
from partition import parse_partition_file
from greedy import GreedySolver
from ortools_solver import IntegerProgrammingSolver
from dp_solver import DPSolver
from MAC_AC3 import CSPSolver


def analyze_partition(partition, instance_id=0):
    """Analisa uma partição usando todos os métodos"""
    
    print(f"\n=== Instância {instance_id} ===")
    print(f"Retângulos: {len(partition.rectangles)}, Vértices: {len(partition.vertices)}")
    
    results = {}
    
    # Greedy
    try:
        solver = GreedySolver(partition)
        _, n1, t1 = solver.max_coverage_greedy()
        _, n2, t2 = solver.min_degree_greedy()
        _, n3, t3 = solver.frequency_weighted_greedy()
        
        results['greedy'] = {
            'max_coverage': n1,
            'min_degree': n2,
            'frequency': n3
        }
        print(f"Greedy: {n1}, {n2}, {n3} guardas")
    except Exception as e:
        print(f"Erro Greedy: {e}")
    
    # OR-Tools
    try:
        solver = IntegerProgrammingSolver(partition)
        _, n, t, status = solver.solve_with_ortools(time_limit=120.0)
        results['ortools'] = {'guards': n, 'time': t, 'status': status}
        print(f"OR-Tools: {n} guardas ({status})")
    except Exception as e:
        print(f"Erro OR-Tools: {e}")
    
    # DP
    try:
        solver = DPSolver(partition)
        
        if len(partition.rectangles) <= 15:
            _, n, t, status = solver.solve_exact_dp()
            results['dp_exact'] = n
            print(f"DP Exato: {n} guardas")
        
        _, n, t, status = solver.solve_greedy_dp()
        results['dp_greedy'] = n
        print(f"DP Greedy: {n} guardas")
        
    except Exception as e:
        print(f"Erro DP: {e}")
    
    # CSP (só para n pequeno)
    if len(partition.rectangles) <= 10:
        try:
            solver = CSPSolver(partition)
            _, n, t, status = solver.solve(time_limit=120.0)
            results['csp'] = n
            print(f"CSP: {n} guardas")
        except Exception as e:
            print(f"Erro CSP: {e}")
    
    return results


def main():
    print("\n=== Vigilância de Partições Retangulares ===\n")
    
    # Carregar dados
    try:
        partitions = parse_partition_file("PartsRectangulares/Exemplos/step50")
        print(f"Carregadas {len(partitions)} instâncias")
    except FileNotFoundError:
        print("Erro: Ficheiro não encontrado")
        return
    
    # Processar
    all_results = {}
    for i in range(min(2, len(partitions))):
        results = analyze_partition(partitions[i], i)
        all_results[f'instance_{i}'] = results
    
    # Salvar
    Path("results").mkdir(exist_ok=True)
    with open("results/results.json", 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print("\nResultados salvos em: results/results.json")


if __name__ == "__main__":
    main()