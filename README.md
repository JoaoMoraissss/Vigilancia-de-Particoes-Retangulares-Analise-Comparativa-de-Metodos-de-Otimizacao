# Vigilância de Partições Retangulares

Projeto de Métodos de Apoio à Decisão (MAD) - CC3003 2025/2026

## 📋 Descrição

Implementação e comparação de métodos para resolver o problema de vigilância de partições retangulares: determinar o número mínimo de guardas em vértices para cobrir todos os retângulos.

## 🎯 Métodos Implementados

- **Greedy**: 4 variantes (Max Coverage, Min Degree, Frequency Weighted, Random)
- **Programação Inteira**: OR-Tools (solução ótima)
- **Programação por Restrições**: MAC + AC-3 (implementação do zero)
- **Programação Dinâmica**: 3 abordagens (Exato, Greedy Híbrido, Bottom-up)

## 📊 Resultados

Para instâncias com 40 retângulos:
- **Solução Ótima (OR-Tools)**: 14 guardas em ~12ms
- **Melhor Greedy (Min Degree)**: 15 guardas em <1ms (+7%)
- **DP Greedy**: 15-17 guardas em ~450ms

## 🚀 Como Executar

### Instalar dependências:
```bash
pip install networkx ortools
```

### Executar:
```bash
python main.py
```
