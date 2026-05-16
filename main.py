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

    print(f"\n{'='*70}")
    print(f"INSTÂNCIA {instance_id}")
    print(f"{'='*70}")
    print(f"Retângulos: {len(partition.rectangles)}, Vértices: {len(partition.vertices)}\n")

    results = {}

    # Greedy
    print("--- GREEDY ---")
    try:
        solver = GreedySolver(partition)

        g1, n1, t1 = solver.max_coverage_greedy()
        g2, n2, t2 = solver.min_degree_greedy()
        g3, n3, t3 = solver.frequency_weighted_greedy()

        print(f"  Max Coverage:       {n1} guardas")
        print(f"  Min Degree:         {n2} guardas")
        print(f"  Frequency Weighted: {n3} guardas")

        results['greedy'] = {
            'max_coverage': {'num': n1, 'guards': [str(g) for g in g1]},
            'min_degree': {'num': n2, 'guards': [str(g) for g in g2]},
            'frequency': {'num': n3, 'guards': [str(g) for g in g3]}
        }
    except Exception as e:
        print(f"  Erro: {e}")

    # OR-Tools
    print("\n--- OR-TOOLS (Programação Inteira) ---")
    try:
        solver = IntegerProgrammingSolver(partition)
        guards, n, t, status = solver.solve_with_ortools(time_limit=120.0)
        print(f"  Guardas: {n} ({status}, {t:.4f}s)")
        results['ortools'] = {'num': n, 'guards': [str(g) for g in guards], 'status': status, 'time': t}
    except Exception as e:
        print(f"  Erro: {e}")

    # DP
    print("\n--- PROGRAMAÇÃO DINÂMICA ---")
    try:
        solver = DPSolver(partition)
        print(f"  Processando {len(partition.rectangles)} retângulos (2^{len(partition.rectangles)} estados)...")
        guards, n, t = solver.solve(verbose=False)
        print(f"  Guardas: {n} ({t:.4f}s)")
        results['dp'] = {'num': n, 'guards': [str(g) for g in guards], 'time': t}
    except MemoryError:
        print(f"  ERRO: Memória insuficiente!")
    except Exception as e:
        print(f"  Erro: {e}")

    # CSP
    print("\n--- CSP (MAC + AC-3) ---")
    try:
        solver = CSPSolver(partition)
        print(f"  Processando {len(partition.rectangles)} retângulos (pode demorar muito)...")
        guards, n, t, status = solver.solve(time_limit=300.0)
        print(f"  Guardas: {n} ({t:.4f}s)")
        results['csp'] = {'num': n, 'guards': [str(g) for g in guards], 'time': t}
    except MemoryError:
        print(f"  ERRO: Memória insuficiente!")
    except Exception as e:
        print(f"  Erro: {e}")

    print(f"\n{'='*70}\n")
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