"""
gerar_graficos.py
=================
Gera gráficos comparativos automaticamente a partir do arquivo de resultados
do problema de distribuição de tarefas entre máquinas.

Uso:
    python gerar_graficos.py                          # usa o .txt mais recente na pasta
    python gerar_graficos.py Resultado_15_02_2026.txt # ou especifica o arquivo
"""

import sys
import os
import glob
import csv
import io
import math
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from collections import defaultdict

# ── Estilo ──────────────────────────────────────────────────────────────────
matplotlib.rcParams.update({
    'figure.facecolor':  '#0d1117',
    'axes.facecolor':    '#161b22',
    'axes.edgecolor':    '#30363d',
    'axes.labelcolor':   '#8b949e',
    'axes.titlecolor':   '#e6edf3',
    'xtick.color':       '#8b949e',
    'ytick.color':       '#8b949e',
    'grid.color':        '#21262d',
    'grid.linewidth':    0.8,
    'text.color':        '#e6edf3',
    'legend.facecolor':  '#161b22',
    'legend.edgecolor':  '#30363d',
    'font.family':       'monospace',
    'font.size':         10,
    'axes.titlesize':    12,
    'axes.labelsize':    10,
})

PALETTE = {
    'Monótona primeira escolha': '#38bdf8',   # azul
    'Monótona melhor escolha':   '#f87171',   # vermelho
    'BLM randomizada':           '#86efac',   # verde
}
MARKERS = {
    'Monótona primeira escolha': 'o',
    'Monótona melhor escolha':   's',
    'BLM randomizada':           '^',
}


# ── Leitura ─────────────────────────────────────────────────────────────────
def encontrar_arquivo():
    """Encontra o .txt de resultado mais recente nas pastas comuns de resultados."""
    # Lista de pastas onde procurar (em ordem de prioridade)
    pastas_candidatas = [
        "Resultados_Tarefas",                               # Subpasta relativa ao script
        os.path.join("Resultados", "Resultados_Tarefas"),  # Se rodar de fora da pasta Resultados
        ".",                                                # Pasta atual do script
    ]
    
    for pasta in pastas_candidatas:
        if os.path.isdir(pasta):
            padrao = os.path.join(pasta, "Resultado*.txt")
            arquivos = glob.glob(padrao)
            if arquivos:
                arquivos = [os.path.normpath(a) for a in arquivos]
                arquivo = max(arquivos, key=os.path.getmtime)
                print(f'   Encontrado em: {os.path.dirname(arquivo)}/')
                return arquivo
    
    # Busca recursiva a partir do diretório atual (até 3 níveis de profundidade)
    print('   Buscando recursivamente...')
    for root, dirs, files in os.walk('.'):
        # Limita profundidade para não demorar muito
        depth = root.count(os.sep)
        if depth > 3:
            continue
        
        for file in files:
            if file.startswith('Resultado') and file.endswith('.txt'):
                caminho = os.path.normpath(os.path.join(root, file))
                print(f'   Encontrado em: {os.path.dirname(caminho)}/')
                return caminho
    
    # Última tentativa: qualquer .txt na pasta atual
    arquivos = glob.glob("*.txt")
    if arquivos:
        arquivos = [os.path.normpath(a) for a in arquivos]
        return max(arquivos, key=os.path.getmtime)
    
    sys.exit("Nenhum arquivo .txt encontrado. Passe o caminho completo como argumento:\n"
             "   python gerar_graficos.py \"caminho\\completo\\Resultado.txt\"")


def ler_dados(caminho):
    """Lê o arquivo de resultados e retorna lista de dicionários."""
    registros = []
    with open(caminho, encoding='utf-8-sig') as f:
        conteudo = f.read()

    # Normaliza line endings Windows (CRLF → LF)
    conteudo = conteudo.replace('\r\n', '\n').replace('\r', '\n')

    linhas = conteudo.strip().splitlines()
    for linha in linhas:
        linha = linha.strip()
        if not linha or linha.lower().startswith('heur'):
            continue

        partes = [p.strip() for p in linha.split(',')]
        # O arquivo tem formato:
        # heuristica, n, m, rep, INTEIRO,DECIMAL ms, iteracoes, mk_i, mk_f, alpha
        # A vírgula decimal do tempo divide o campo em dois → temos 10 partes
        if len(partes) < 9:
            continue

        try:
            heuristica = partes[0]
            n          = int(partes[1])
            m          = int(partes[2])
            rep        = int(partes[3])

            # Detecta se o tempo foi partido em dois (vírgula decimal)
            # Tentamos: partes[4] = inteiro, partes[5] = "decimal ms"
            if 'ms' in partes[5] if len(partes) > 5 else False:
                tempo_raw  = partes[4] + '.' + partes[5].replace(' ms', '').strip()
                tempo      = float(tempo_raw)
                offset     = 1   # deslocamento dos índices seguintes
            else:
                tempo      = float(partes[4].replace(',', '.').replace(' ms', '').strip())
                offset     = 0

            iteracoes  = int(partes[5 + offset])
            mk_inicial = int(partes[6 + offset])
            mk_final   = int(partes[7 + offset])
            alpha_str  = partes[8 + offset].strip()
            alpha      = None if alpha_str.upper() == 'NA' else float(alpha_str.replace(',', '.'))

            registros.append({
                'heuristica': heuristica,
                'n': n, 'm': m, 'rep': rep,
                'tempo': tempo,
                'iteracoes': iteracoes,
                'mk_inicial': mk_inicial,
                'mk_final': mk_final,
                'alpha': alpha,
                'reducao_pct': (mk_inicial - mk_final) / mk_inicial * 100,
                'razao': mk_final / mk_inicial,
            })
        except (ValueError, IndexError):
            continue

    return registros


def agrupar(registros, chave='heuristica'):
    grupos = defaultdict(list)
    for r in registros:
        grupos[r[chave]].append(r)
    return dict(grupos)


def media(lst, campo):
    vals = [r[campo] for r in lst]
    return sum(vals) / len(vals) if vals else 0


def cor(h):
    return PALETTE.get(h, '#a78bfa')


def marcador(h):
    return MARKERS.get(h, 'D')


# ── Helpers de plot ──────────────────────────────────────────────────────────
def barra_comparativa(ax, grupos, campo, titulo, ylabel, log=False, fmt=None):
    heuristicas = list(grupos.keys())
    medias = [media(grupos[h], campo) for h in heuristicas]
    cores  = [cor(h) for h in heuristicas]
    labels = [h.replace(' ', '\n') for h in heuristicas]

    bars = ax.bar(labels, medias, color=cores, edgecolor='none', width=0.5, zorder=3)
    ax.set_title(titulo)
    ax.set_ylabel(ylabel)
    ax.grid(axis='y', zorder=0)
    if log:
        ax.set_yscale('log')

    # Renderiza primeiro para obter os limites reais do eixo
    ax.figure.canvas.draw()
    y_min, y_max = ax.get_ylim()

    import math as _math
    for bar, val in zip(bars, medias):
        label = fmt(val) if fmt else f'{val:.2f}'
        h = bar.get_height()

        if log:
            log_min = _math.log10(max(y_min, 1e-9))
            log_max = _math.log10(y_max)
            log_h   = _math.log10(max(h, 1e-9))
            frac    = (log_h - log_min) / (log_max - log_min)  # 0..1
        else:
            frac = (h - y_min) / (y_max - y_min)

        LIMIAR = 0.18  # barra ocupa menos de 18% do eixo → texto fora (acima)

        if frac >= LIMIAR:
            # Dentro da barra: posiciona mais próximo do topo
            if log:
                # Em log, calcula posição que seja 85-90% da altura logarítmica
                # Convertendo de volta para escala linear
                log_pos = log_h - (log_h - log_min) * 0.12  # 12% abaixo do topo (em log)
                y_pos = 10 ** log_pos
                # Garante que não caia abaixo do mínimo visível
                y_pos = max(y_pos, y_min * 1.2)
            else:
                y_pos = h * 0.92  # 92% da altura
            ax.text(bar.get_x() + bar.get_width() / 2, y_pos,
                    label, ha='center', va='top',
                    fontsize=9, color='#0d1117', fontweight='bold')
        else:
            # Fora da barra, logo acima — garante que não ultrapasse y_max
            if log:
                y_pos = min(h * 1.5, y_max * 0.85)
            else:
                y_pos = h + (y_max - y_min) * 0.02
            ax.text(bar.get_x() + bar.get_width() / 2, y_pos,
                    label, ha='center', va='bottom',
                    fontsize=9, color='#e6edf3', fontweight='bold')
    return ax


def scatter_vs_n(ax, grupos, campo, titulo, ylabel, log=False):
    for h, dados in grupos.items():
        xs = [d['n'] for d in dados]
        ys = [d[campo] for d in dados]
        ax.scatter(xs, ys, color=cor(h), marker=marcador(h),
                   label=h, s=60, zorder=3, alpha=0.9)
    ax.set_title(titulo)
    ax.set_xlabel('n (número de tarefas)')
    ax.set_ylabel(ylabel)
    ax.legend(fontsize=8)
    ax.grid(zorder=0)
    if log:
        ax.set_yscale('log')


# ── Figura 1: Visão Geral (2×3) ──────────────────────────────────────────────
def fig_visao_geral(registros, grupos, destino):
    fig = plt.figure(figsize=(18, 11))
    fig.suptitle('Comparação de Heurísticas — Visão Geral',
                 fontsize=15, fontweight='bold', y=0.98)

    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

    # 1. Redução de makespan média
    ax1 = fig.add_subplot(gs[0, 0])
    barra_comparativa(ax1, grupos, 'reducao_pct',
                      'Redução Média de Makespan', '%',
                      fmt=lambda v: f'{v:.1f}%')

    # 2. Tempo médio de execução
    ax2 = fig.add_subplot(gs[0, 1])
    barra_comparativa(ax2, grupos, 'tempo',
                      'Tempo Médio de Execução', 'ms (log)',
                      log=True, fmt=lambda v: f'{v:.2f} ms')

    # 3. Iterações médias
    ax3 = fig.add_subplot(gs[0, 2])
    barra_comparativa(ax3, grupos, 'iteracoes',
                      'Iterações Médias', 'iterações (log)',
                      log=True, fmt=lambda v: f'{int(v):,}'.replace(',', '.'))

    # 4. Makespan final por replicação (linha)
    ax4 = fig.add_subplot(gs[1, :2])
    for h, dados in grupos.items():
        dados_ord = sorted(dados, key=lambda d: d['rep'])
        xs = [d['rep'] for d in dados_ord]
        ys = [d['mk_final'] for d in dados_ord]
        ax4.plot(xs, ys, color=cor(h), marker=marcador(h),
                 label=h, linewidth=1.8, markersize=6, zorder=3)
    ax4.set_title('Makespan Final por Replicação')
    ax4.set_xlabel('Replicação')
    ax4.set_ylabel('Makespan Final (log)')
    ax4.set_yscale('log')
    ax4.legend(fontsize=8)
    ax4.grid(zorder=0)

    # 5. Razão mk_final / mk_inicial
    ax5 = fig.add_subplot(gs[1, 2])
    barra_comparativa(ax5, grupos, 'razao',
                      'Razão Final/Inicial\n(menor = melhor)', 'razão',
                      fmt=lambda v: f'{v*100:.1f}%')

    _salvar(fig, destino, 'fig1_visao_geral.png')


# ── Figura 2: Tempo de Execução ──────────────────────────────────────────────
def fig_tempo(registros, grupos, destino):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('Análise de Tempo de Execução', fontsize=14, fontweight='bold')
    fig.patch.set_facecolor('#0d1117')

    # Scatter: tempo por experimento
    ax = axes[0]
    for i, (h, dados) in enumerate(grupos.items()):
        xs = [i + np.random.uniform(-0.15, 0.15) for _ in dados]  # jitter
        ys = [d['tempo'] for d in dados]
        ax.scatter(xs, ys, color=cor(h), marker=marcador(h), s=70, alpha=0.85, zorder=3)
    ax.set_xticks(range(len(grupos)))
    ax.set_xticklabels([h.replace(' ', '\n') for h in grupos], fontsize=9)
    ax.set_yscale('log')
    ax.set_title('Distribuição de Tempo (cada ponto = 1 replicação)')
    ax.set_ylabel('Tempo (ms, log)')
    ax.grid(zorder=0)

    # Scatter: tempo vs n
    scatter_vs_n(axes[1], grupos, 'tempo',
                 'Tempo × Tamanho da Instância (n)',
                 'Tempo (ms, log)', log=True)

    plt.tight_layout()
    _salvar(fig, destino, 'fig2_tempo.png')


# ── Figura 3: Qualidade — Makespan ───────────────────────────────────────────
def fig_makespan(registros, grupos, destino):
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('Análise de Qualidade — Makespan', fontsize=14, fontweight='bold')
    fig.patch.set_facecolor('#0d1117')

    # Inicial vs Final agrupado
    ax = axes[0]
    heuristicas = list(grupos.keys())
    x = np.arange(len(heuristicas))
    w = 0.35
    medias_i = [media(grupos[h], 'mk_inicial') for h in heuristicas]
    medias_f = [media(grupos[h], 'mk_final')   for h in heuristicas]
    bars_i = ax.bar(x - w/2, medias_i, w, color='#f5a623', alpha=0.6, label='Inicial', zorder=3)
    bars_f = ax.bar(x + w/2, medias_f, w, color=[cor(h) for h in heuristicas], alpha=0.9,
           label='Final', zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels([h.replace(' ', '\n') for h in heuristicas], fontsize=8)
    ax.set_yscale('log')
    ax.set_title('Makespan Inicial vs Final (média)')
    ax.set_ylabel('Makespan (log)')
    ax.legend(fontsize=8)
    ax.grid(axis='y', zorder=0)
    
    # Adiciona rótulos nas barras
    ax.figure.canvas.draw()
    y_min, y_max = ax.get_ylim()
    import math as _math
    
    # Rótulos para barras iniciais (laranjas)
    for bar, val in zip(bars_i, medias_i):
        h = bar.get_height()
        log_min = _math.log10(max(y_min, 1e-9))
        log_max = _math.log10(max(y_max, 1e-9))
        log_h   = _math.log10(max(h, 1e-9))
        log_pos = log_h - (log_h - log_min) * 0.12
        y_pos = max(10 ** log_pos, y_min * 1.2)
        ax.text(bar.get_x() + bar.get_width() / 2, y_pos,
                f'{int(val):,}'.replace(',', '.'),
                ha='center', va='top', fontsize=8, 
                color='#0d1117', fontweight='bold')
    
    # Rótulos para barras finais (coloridas)
    for bar, val in zip(bars_f, medias_f):
        h = bar.get_height()
        log_h   = _math.log10(max(h, 1e-9))
        log_pos = log_h - (log_h - log_min) * 0.12
        y_pos = max(10 ** log_pos, y_min * 1.2)
        ax.text(bar.get_x() + bar.get_width() / 2, y_pos,
                f'{int(val):,}'.replace(',', '.'),
                ha='center', va='top', fontsize=8,
                color='#0d1117', fontweight='bold')

    # Scatter: makespan final vs n
    scatter_vs_n(axes[1], grupos, 'mk_final',
                 'Makespan Final × n',
                 'Makespan Final (log)', log=True)

    # Boxplot de redução %
    ax3 = axes[2]
    dados_box = [[ d['reducao_pct'] for d in grupos[h] ] for h in heuristicas]
    bp = ax3.boxplot(dados_box, patch_artist=True,
                     medianprops=dict(color='#fff', linewidth=2),
                     whiskerprops=dict(color='#555'),
                     capprops=dict(color='#555'),
                     flierprops=dict(marker='o', markersize=5, markerfacecolor='#fff', 
                                     markeredgecolor='#fff', alpha=0.8))
    for patch, h in zip(bp['boxes'], heuristicas):
        patch.set_facecolor(cor(h))
        patch.set_alpha(0.7)
    ax3.set_xticklabels([h.replace(' ', '\n') for h in heuristicas], fontsize=8)
    ax3.set_title('Distribuição da Redução de Makespan (%)')
    ax3.set_ylabel('Redução (%)')
    ax3.grid(axis='y', zorder=0)

    plt.tight_layout()
    _salvar(fig, destino, 'fig3_makespan.png')


# ── Figura 4: Iterações ───────────────────────────────────────────────────────
def fig_iteracoes(registros, grupos, destino):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('Análise de Iterações', fontsize=14, fontweight='bold')
    fig.patch.set_facecolor('#0d1117')

    # Barras agrupadas por replicação
    ax = axes[0]
    heuristicas = list(grupos.keys())
    n_reps = max(len(v) for v in grupos.values())
    x = np.arange(n_reps)
    w = 0.28
    for i, h in enumerate(heuristicas):
        dados_ord = sorted(grupos[h], key=lambda d: d['rep'])
        ys = [d['iteracoes'] for d in dados_ord]
        ax.bar(x[:len(ys)] + i*w - w, ys, w,
               color=cor(h), alpha=0.85, label=h, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels([f'Rep {i}' for i in range(n_reps)], fontsize=7, rotation=45)
    ax.set_yscale('log')
    ax.set_title('Iterações por Replicação')
    ax.set_ylabel('Iterações (log)')
    ax.legend(fontsize=8)
    ax.grid(axis='y', zorder=0)

    # Scatter: iterações vs n
    scatter_vs_n(axes[1], grupos, 'iteracoes',
                 'Iterações × Tamanho da Instância (n)',
                 'Iterações (log)', log=True)

    plt.tight_layout()
    _salvar(fig, destino, 'fig4_iteracoes.png')


# ── Figura 5: Painel completo (para apresentação) ────────────────────────────
def fig_painel(registros, grupos, destino):
    fig = plt.figure(figsize=(20, 14))
    fig.suptitle('Painel Geral — Heurísticas para Distribuição de Tarefas',
                 fontsize=16, fontweight='bold', y=0.99)
    fig.patch.set_facecolor('#0d1117')

    gs = gridspec.GridSpec(3, 4, figure=fig, hspace=0.50, wspace=0.38)

    # Linha 1: cards de resumo como barras horizontais simples
    metricas = [
        ('reducao_pct', 'Redução Makespan (%)',  lambda v: f'{v:.1f}%',   False),
        ('tempo',       'Tempo Médio (ms)',       lambda v: f'{v:.2f}',    True),
        ('iteracoes',   'Iterações Médias',       lambda v: f'{int(v):,}'.replace(',','.'), True),
    ]

    for col, (campo, titulo, fmt, log) in enumerate(metricas):
        ax = fig.add_subplot(gs[0, col])
        barra_comparativa(ax, grupos, campo, titulo,
                          '' if col > 0 else 'valor',
                          log=log, fmt=fmt)

    # Makespan final/inicial side-by-side
    ax_mk = fig.add_subplot(gs[0, 3])
    heuristicas = list(grupos.keys())
    x = np.arange(len(heuristicas))
    w = 0.35
    medias_i = [media(grupos[h], 'mk_inicial') for h in heuristicas]
    medias_f = [media(grupos[h], 'mk_final') for h in heuristicas]
    bars_i = ax_mk.bar(x - w/2, medias_i,
              w, color='#f5a623', alpha=0.55, label='Inicial', zorder=3)
    bars_f = ax_mk.bar(x + w/2, medias_f,
              w, color=[cor(h) for h in heuristicas], alpha=0.9, label='Final', zorder=3)
    ax_mk.set_xticks(x)
    ax_mk.set_xticklabels([h.replace(' ', '\n') for h in heuristicas], fontsize=7)
    ax_mk.set_yscale('log')
    ax_mk.set_title('Makespan Inicial vs Final')
    ax_mk.legend(fontsize=7)
    ax_mk.grid(axis='y', zorder=0)
    
    # Adiciona rótulos nas barras
    ax_mk.figure.canvas.draw()
    y_min, y_max = ax_mk.get_ylim()
    import math as _math
    log_min = _math.log10(max(y_min, 1e-9))
    log_max = _math.log10(max(y_max, 1e-9))
    
    for bar, val in zip(bars_i, medias_i):
        h = bar.get_height()
        log_h = _math.log10(max(h, 1e-9))
        log_pos = log_h - (log_h - log_min) * 0.12
        y_pos = max(10 ** log_pos, y_min * 1.2)
        ax_mk.text(bar.get_x() + bar.get_width() / 2, y_pos,
                   f'{int(val):,}'.replace(',', '.'),
                   ha='center', va='top', fontsize=7,
                   color='#0d1117', fontweight='bold')
    
    for bar, val in zip(bars_f, medias_f):
        h = bar.get_height()
        log_h = _math.log10(max(h, 1e-9))
        log_pos = log_h - (log_h - log_min) * 0.12
        y_pos = max(10 ** log_pos, y_min * 1.2)
        ax_mk.text(bar.get_x() + bar.get_width() / 2, y_pos,
                   f'{int(val):,}'.replace(',', '.'),
                   ha='center', va='top', fontsize=7,
                   color='#0d1117', fontweight='bold')
    ax_mk.grid(axis='y', zorder=0)

    # Linha 2: scatter tempo×n e iterações×n
    ax_tn = fig.add_subplot(gs[1, :2])
    scatter_vs_n(ax_tn, grupos, 'tempo',
                 'Tempo × n', 'Tempo (ms, log)', log=True)

    ax_in = fig.add_subplot(gs[1, 2:])
    scatter_vs_n(ax_in, grupos, 'iteracoes',
                 'Iterações × n', 'Iterações (log)', log=True)

    # Linha 3: makespan final por replicação + boxplot redução
    ax_line = fig.add_subplot(gs[2, :3])
    for h, dados in grupos.items():
        dados_ord = sorted(dados, key=lambda d: d['rep'])
        xs = [d['rep'] for d in dados_ord]
        ys = [d['mk_final'] for d in dados_ord]
        ax_line.plot(xs, ys, color=cor(h), marker=marcador(h),
                     label=h, linewidth=2, markersize=7, zorder=3)
    ax_line.set_title('Makespan Final por Replicação')
    ax_line.set_xlabel('Replicação')
    ax_line.set_ylabel('Makespan Final (log)')
    ax_line.set_yscale('log')
    ax_line.legend(fontsize=8)
    ax_line.grid(zorder=0)

    ax_box = fig.add_subplot(gs[2, 3])
    dados_box = [[d['reducao_pct'] for d in grupos[h]] for h in heuristicas]
    bp = ax_box.boxplot(dados_box, patch_artist=True,
                        medianprops=dict(color='#fff', linewidth=2),
                        whiskerprops=dict(color='#555'), capprops=dict(color='#555'),
                        flierprops=dict(marker='o', markersize=5, markerfacecolor='#fff',
                                        markeredgecolor='#fff', alpha=0.8))
    for patch, h in zip(bp['boxes'], heuristicas):
        patch.set_facecolor(cor(h))
        patch.set_alpha(0.7)
    ax_box.set_xticklabels([h.replace(' ', '\n') for h in heuristicas], fontsize=7)
    ax_box.set_title('Redução de Makespan (%)')
    ax_box.set_ylabel('%')
    ax_box.grid(axis='y', zorder=0)

    _salvar(fig, destino, 'fig5_painel_completo.png')


# ── Salvar ────────────────────────────────────────────────────────────────────
def _salvar(fig, destino, nome):
    caminho = os.path.join(destino, nome)
    fig.savefig(caminho, dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f'  OK  {caminho}')


# ── Respostas do enunciado ───────────────────────────────────────────────────
def imprimir_respostas(grupos):
    print('\n' + '='*60)
    print('  RESPOSTAS — QUESTÕES DO ENUNCIADO')
    print('='*60)

    def melhor(campo, inverso=False):
        medias = {h: media(v, campo) for h, v in grupos.items()}
        return (min if inverso else max)(medias, key=medias.get), medias

    h_iter, medias_iter = melhor('iteracoes')
    print(f'\n▸ Mais iterações:   {h_iter}')
    for h, v in medias_iter.items():
        print(f'    {h:<35} {int(v):>8,}'.replace(',','.') + ' iter')

    h_tempo, medias_tempo = melhor('tempo')
    print(f'\n▸ Mais tempo:       {h_tempo}')
    for h, v in medias_tempo.items():
        print(f'    {h:<35} {v:>10.4f} ms')

    h_qual, medias_qual = melhor('reducao_pct')
    print(f'\n▸ Maior qualidade:  {h_qual}')
    for h, v in medias_qual.items():
        print(f'    {h:<35} {v:>8.2f}% redução')

    print('='*60 + '\n')


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) > 1:
        caminho_arquivo = os.path.normpath(sys.argv[1])
    else:
        caminho_arquivo = encontrar_arquivo()
    
    print(f'\nLendo: {caminho_arquivo}')

    registros = ler_dados(caminho_arquivo)
    if not registros:
        sys.exit('Nenhum registro válido encontrado no arquivo.')

    print(f'   {len(registros)} registros carregados.')

    grupos = agrupar(registros)
    print(f'   Heurísticas: {list(grupos.keys())}')

    # Pasta de saída ao lado do arquivo de resultado
    base = os.path.splitext(caminho_arquivo)[0]
    destino = base + '_graficos'
    os.makedirs(destino, exist_ok=True)
    print(f'\nGerando graficos em: {destino}/')

    fig_visao_geral(registros, grupos, destino)
    fig_tempo(registros, grupos, destino)
    fig_makespan(registros, grupos, destino)
    fig_iteracoes(registros, grupos, destino)
    fig_painel(registros, grupos, destino)

    imprimir_respostas(grupos)
    print(f'Concluido! {destino}/')


if __name__ == '__main__':
    main()