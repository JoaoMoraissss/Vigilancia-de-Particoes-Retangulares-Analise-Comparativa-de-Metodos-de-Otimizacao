"""
generate_plots.py - Gera todos os gráficos para o relatório
Vigilância de Partições Retangulares - MAD 2025/2026

Como usar:
    python generate_plots.py
    
Ou importar e usar as funções individualmente:
    from generate_plots import plot_comparison
    plot_comparison(results, "meu_grafico.png")
"""

import matplotlib.pyplot as plt
import numpy as np
import os


# ==============================================================================
# CONFIGURAÇÃO GLOBAL
# ==============================================================================

# Criar pasta para gráficos (se não existir)
OUTPUT_DIR = "graficos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Configuração de estilo
plt.rcParams['font.size'] = 11
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10


# ==============================================================================
# GRÁFICO 1: COMPARAÇÃO DE NÚMERO DE GUARDAS
# ==============================================================================

def plot_comparison(results, output_file=None):
    """
    Gráfico de barras comparando número de guardas por método.
    
    Args:
        results: dicionário com formato:
            {
                'max_coverage': 20,
                'min_degree': 21,
                'frequency_weighted': 20,
                'ortools_optimal': 17,
                'dp_greedy': 20
            }
        output_file: nome do ficheiro de saída (default: graficos/fig1_comparacao.png)
    """
    if output_file is None:
        output_file = os.path.join(OUTPUT_DIR, "fig1_comparacao.png")
    
    # Traduzir nomes para labels bonitos
    label_map = {
        'max_coverage': 'Greedy\nMax Coverage',
        'min_degree': 'Greedy\nMin Degree',
        'frequency_weighted': 'Greedy\nFreq. Weighted',
        'random_greedy': 'Greedy\nRandom',
        'ortools_optimal': 'Programação\nInteira (Ótimo)',
        'dp_exact': 'DP\nExato',
        'dp_greedy': 'DP\nGreedy',
        'csp_mac': 'MAC\n+ AC-3'
    }
    
    # Preparar dados
    methods = []
    guards = []
    colors = []
    
    for key, value in results.items():
        methods.append(label_map.get(key, key))
        guards.append(value)
        
        # Cores: verde para ótimo, azul para greedy, laranja para DP, roxo para CSP
        if 'optimal' in key or 'ortools' in key:
            colors.append('#2ecc71')  # Verde
        elif 'greedy' in key or 'coverage' in key or 'degree' in key or 'frequency' in key or 'random' in key:
            colors.append('#3498db')  # Azul
        elif 'dp' in key:
            colors.append('#f39c12')  # Laranja
        elif 'csp' in key or 'mac' in key:
            colors.append('#9b59b6')  # Roxo
        else:
            colors.append('#95a5a6')  # Cinza
    
    # Criar gráfico
    fig, ax = plt.subplots(figsize=(12, 7))
    
    bars = ax.bar(methods, guards, color=colors, edgecolor='black', 
                  linewidth=1.5, alpha=0.8)
    
    # Adicionar valores no topo das barras
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{int(height)}',
               ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # Linha horizontal no ótimo (se existir)
    optimal_keys = [k for k in results.keys() if 'optimal' in k or 'ortools' in k]
    if optimal_keys:
        optimal_value = results[optimal_keys[0]]
        ax.axhline(y=optimal_value, color='green', linestyle='--', 
                  linewidth=2, alpha=0.5, label=f'Solução Ótima = {optimal_value}')
        ax.legend(loc='upper right')
    
    # Configurações do gráfico
    ax.set_ylabel('Número de Guardas', fontsize=14, fontweight='bold')
    ax.set_title('Comparação de Métodos: Número de Guardas', 
                fontsize=16, fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_ylim(0, max(guards) * 1.15)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Gráfico salvo: {output_file}")
    plt.close()


# ==============================================================================
# GRÁFICO 2: COMPARAÇÃO DE TEMPO DE EXECUÇÃO
# ==============================================================================

def plot_time_comparison(times, output_file=None):
    """
    Gráfico de barras comparando tempo de execução.
    
    Args:
        times: dicionário com formato:
            {
                'max_coverage': 0.0008,
                'min_degree': 0.0002,
                'ortools_optimal': 0.0155
            }
        output_file: nome do ficheiro (default: graficos/fig2_tempo.png)
    """
    if output_file is None:
        output_file = os.path.join(OUTPUT_DIR, "fig2_tempo.png")
    
    label_map = {
        'max_coverage': 'Greedy\nMax Cov',
        'min_degree': 'Greedy\nMin Deg',
        'frequency_weighted': 'Greedy\nFreq. W.',
        'ortools_optimal': 'PI\nOR-Tools',
        'dp_exact': 'DP\nExato',
        'dp_greedy': 'DP\nGreedy',
        'csp_mac': 'CSP\nMAC'
    }
    
    methods = [label_map.get(k, k) for k in times.keys()]
    time_values = list(times.values())
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.bar(methods, time_values, color='#e74c3c', 
                  edgecolor='black', linewidth=1.5, alpha=0.8)
    
    # Valores nas barras
    for bar in bars:
        height = bar.get_height()
        # Formato adaptativo: se < 0.01s usar notação científica
        if height < 0.01:
            label = f'{height:.2e}s'
        else:
            label = f'{height:.4f}s'
        
        ax.text(bar.get_x() + bar.get_width()/2., height,
               label, ha='center', va='bottom', 
               fontsize=11, fontweight='bold')
    
    ax.set_ylabel('Tempo de Execução (segundos)', fontsize=14, fontweight='bold')
    ax.set_title('Comparação de Tempo de Execução', 
                fontsize=16, fontweight='bold', pad=20)
    ax.set_yscale('log')  # Escala logarítmica (diferenças grandes)
    ax.grid(axis='y', alpha=0.3, which='both')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Gráfico salvo: {output_file}")
    plt.close()


# ==============================================================================
# GRÁFICO 3: QUALIDADE VS TEMPO (SCATTER)
# ==============================================================================

def plot_quality_vs_time(results_full, optimal, output_file=None):
    """
    Scatter plot: qualidade (gap vs ótimo) vs tempo de execução.
    
    Args:
        results_full: dicionário com formato:
            {
                'max_coverage': {'guards': 20, 'time': 0.0008},
                'ortools': {'guards': 17, 'time': 0.0155}
            }
        optimal: número de guardas na solução ótima
        output_file: nome do ficheiro (default: graficos/fig3_tradeoff.png)
    """
    if output_file is None:
        output_file = os.path.join(OUTPUT_DIR, "fig3_tradeoff.png")
    
    label_map = {
        'max_coverage': 'Greedy Max Cov',
        'min_degree': 'Greedy Min Deg',
        'frequency_weighted': 'Greedy Freq W',
        'ortools': 'PI OR-Tools',
        'dp_greedy': 'DP Greedy'
    }
    
    color_map = {
        'max_coverage': '#3498db',
        'min_degree': '#3498db',
        'frequency_weighted': '#3498db',
        'ortools': '#2ecc71',
        'dp_greedy': '#f39c12'
    }
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    for method, data in results_full.items():
        time = data['time']
        guards = data['guards']
        
        # Calcular gap vs ótimo
        gap = ((guards - optimal) / optimal * 100) if optimal > 0 else 0
        
        color = color_map.get(method, '#95a5a6')
        label = label_map.get(method, method)
        
        # Plotar ponto
        ax.scatter(time, gap, s=300, color=color, 
                  edgecolor='black', linewidth=2, alpha=0.7, 
                  label=label, zorder=3)
        
        # Anotar
        ax.annotate(label, (time, gap), 
                   xytext=(10, 10), textcoords='offset points',
                   fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', 
                            facecolor=color, alpha=0.3))
    
    # Linha no gap=0 (ótimo)
    ax.axhline(y=0, color='green', linestyle='--', 
              linewidth=2, alpha=0.7, label='Solução Ótima', zorder=1)
    
    ax.set_xlabel('Tempo de Execução (segundos)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Gap vs Ótimo (%)', fontsize=14, fontweight='bold')
    ax.set_title('Trade-off: Qualidade vs Velocidade', 
                fontsize=16, fontweight='bold', pad=20)
    ax.set_xscale('log')
    ax.grid(True, alpha=0.3, linestyle='--', zorder=0)
    ax.legend(loc='best', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico salvo: {output_file}")
    plt.close()


# ==============================================================================
# GRÁFICO 4: EXTENSÃO 4b - ALCANCE DOS GUARDAS
# ==============================================================================

def plot_range_extension(distances, guards_counts, output_file=None):
    """
    Gráfico mostrando impacto do alcance D no número de guardas.
    
    Args:
        distances: lista de distâncias [0, 1, 2]
        guards_counts: lista de guardas [17, 5, 2]
        output_file: nome do ficheiro (default: graficos/fig4_extensao_alcance.png)
    """
    if output_file is None:
        output_file = os.path.join(OUTPUT_DIR, "fig4_extensao_alcance.png")
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Linha e pontos
    ax.plot(distances, guards_counts, marker='o', markersize=15, 
           linewidth=4, color='#e74c3c', markeredgecolor='black',
           markeredgewidth=2, label='Guardas necessários')
    
    # Anotar pontos
    for d, g in zip(distances, guards_counts):
        ax.annotate(f'{g} guardas', (d, g), 
                   xytext=(0, 20), textcoords='offset points',
                   fontsize=13, fontweight='bold', ha='center',
                   bbox=dict(boxstyle='round,pad=0.5', 
                            facecolor='yellow', alpha=0.7))
    
    # Área sombreada
    ax.fill_between(distances, guards_counts, alpha=0.2, color='#e74c3c')
    
    # Calcular e mostrar redução percentual
    if len(guards_counts) >= 2:
        reduction = (guards_counts[0] - guards_counts[-1]) / guards_counts[0] * 100
        
        # Texto com redução
        mid_x = (distances[0] + distances[-1]) / 2
        mid_y = (guards_counts[0] + guards_counts[-1]) / 2
        
        ax.text(mid_x, mid_y, 
               f'Redução:\n{reduction:.0f}%',
               fontsize=14, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.7', 
                        facecolor='lightgreen', edgecolor='green', 
                        linewidth=2))
    
    ax.set_xlabel('Alcance D (distância no grafo)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Número de Guardas Necessários', fontsize=14, fontweight='bold')
    ax.set_title('Extensão 4b: Impacto do Alcance dos Guardas', 
                fontsize=16, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xticks(distances)
    ax.set_ylim(0, max(guards_counts) * 1.2)
    ax.legend(loc='upper right', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico salvo: {output_file}")
    plt.close()


# ==============================================================================
# GRÁFICO 5: EXTENSÃO 4a - GUARDAS COM CORES
# ==============================================================================

def plot_color_extension(num_guards, num_colors, output_file=None):
    """
    Gráfico mostrando relação guardas vs cores necessárias.
    
    Args:
        num_guards: número de guardas
        num_colors: número de cores necessárias
        output_file: nome do ficheiro (default: graficos/fig5_extensao_cores.png)
    """
    if output_file is None:
        output_file = os.path.join(OUTPUT_DIR, "fig5_extensao_cores.png")
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    categories = ['Guardas', 'Cores\nNecessárias']
    values = [num_guards, num_colors]
    colors_bars = ['#3498db', '#e74c3c']
    
    bars = ax.bar(categories, values, color=colors_bars, 
                  edgecolor='black', linewidth=2, alpha=0.8, width=0.5)
    
    # Valores nas barras
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{int(height)}',
               ha='center', va='bottom', fontsize=16, fontweight='bold')
    
    ax.set_ylabel('Quantidade', fontsize=14, fontweight='bold')
    ax.set_title('Extensão 4a: Guardas com Cores', 
                fontsize=16, fontweight='bold', pad=20)
    ax.set_ylim(0, max(values) * 1.3)
    ax.grid(axis='y', alpha=0.3)
    
    # Texto explicativo
    ratio = num_guards / num_colors if num_colors > 0 else 0
    ax.text(0.5, max(values) * 1.1, 
           f'Razão: {ratio:.1f} guardas/cor',
           ha='center', fontsize=12,
           bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow'))
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico salvo: {output_file}")
    plt.close()


# ==============================================================================
# FUNÇÃO PRINCIPAL - GERA TODOS OS GRÁFICOS
# ==============================================================================

def generate_all_plots():
    """
    Gera todos os gráficos com dados de exemplo.
    Substitui pelos teus dados reais!
    """
    
    print("\n" + "="*70)
    print("  GERADOR DE GRÁFICOS - Vigilância de Partições Retangulares")
    print("="*70 + "\n")
    
    # ========== DADOS DE EXEMPLO (SUBSTITUI PELOS TEUS!) ==========
    
    # 1. Número de guardas por método
    results_guards = {
        'max_coverage': 20,
        'min_degree': 21,
        'frequency_weighted': 20,
        'ortools_optimal': 17,
        'dp_greedy': 20
    }
    
    # 2. Tempo de execução
    results_time = {
        'max_coverage': 0.0008,
        'min_degree': 0.0002,
        'frequency_weighted': 0.0010,
        'ortools_optimal': 0.0155,
        'dp_greedy': 0.4467
    }
    
    # 3. Dados completos (guardas + tempo)
    results_full = {
        'max_coverage': {'guards': 20, 'time': 0.0008},
        'min_degree': {'guards': 21, 'time': 0.0002},
        'frequency_weighted': {'guards': 20, 'time': 0.0010},
        'ortools': {'guards': 17, 'time': 0.0155},
        'dp_greedy': {'guards': 20, 'time': 0.4467}
    }
    
    # 4. Extensão 4b - alcance
    distances = [0, 1, 2]
    guards_by_range = [17, 5, 2]
    
    # 5. Extensão 4a - cores
    num_guards_colored = 17
    num_colors = 1
    
    # ========== GERAR GRÁFICOS ==========
    
    print("📊 Gerando gráficos...\n")
    
    plot_comparison(results_guards)
    plot_time_comparison(results_time)
    plot_quality_vs_time(results_full, optimal=17)
    plot_range_extension(distances, guards_by_range)
    plot_color_extension(num_guards_colored, num_colors)
    
    print("\n" + "="*70)
    print(f"  ✅ Todos os gráficos gerados em: {OUTPUT_DIR}/")
    print("="*70 + "\n")


# ==============================================================================
# EXECUTAR SE CHAMADO DIRETAMENTE
# ==============================================================================

if __name__ == "__main__":
    generate_all_plots()