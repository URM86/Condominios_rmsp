"""
Heatmap: Ano de divulgação de sentenças × Ano de abertura do processo
Paleta inspirada em BBC News / Datawrapper
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.font_manager as fm
import numpy as np
from pathlib import Path

# ── 0. FONTE FIRA SANS ────────────────────────────────────────────────────────
# Tenta carregar Fira Sans; se não encontrar, usa fallback legível
_fira_candidates = [
    f.name for f in fm.fontManager.ttflist if "Fira Sans" in f.name]
FONT = "Fira Sans" if _fira_candidates else "Segoe UI"   # Segoe UI vem no Windows
print(f"✓  Fonte em uso: {FONT}")

# ── 1. LEITURA DOS DADOS ─────────────────────────────────────────────────────

FILE = r"C:\Users\ulise\Condominios_Trabalho\Condominios_rmsp\data\heatmap.csv"
out = r"C:\Users\ulise\Condominios_Trabalho\Condominios_rmsp\output"

df = pd.read_csv(FILE, sep=";", encoding="cp860")

# Colunas de interesse
col_sentenca = df.columns[3]   # "Ano da Sentença"
col_abertura = df.columns[4]   # "Abertura"

# Contagem cruzada: linhas = Abertura, colunas = Ano da Sentença
pivot = (
    df.groupby([col_abertura, col_sentenca])
    .size()
    .unstack(fill_value=0)
)

# Filtra apenas aberturas a partir de 2010
pivot = pivot[pivot.index >= 2010]

# ── 2. PALETA BBC / DATAWRAPPER ──────────────────────────────────────────────

BG = "#FFFFFF"
ZERO_CLR = "#F2F2F2"
TXT_DARK = "#1A1A1A"
TXT_MID = "#5C5C5C"
TXT_LIGHT = "#FFFFFF"
ACCENT = "#1380A1"

cmap_colors = [
    "#E1EAF5",
    "#C9D9EA",
    "#7BAFD4",
    "#3A7CBF",
    "#1A4B99",
    "#0A1F6E",
]
CMAP = mcolors.LinearSegmentedColormap.from_list("dw_blue", cmap_colors, N=512)

# ── 3. PRÉ-PROCESSAMENTO ─────────────────────────────────────────────────────

data = pivot.values.astype(float)
# Rótulos das linhas com quebra de linha em "em"
rows = [f"Abertura\nem {y}" for y in pivot.index]
cols = [str(c) for c in pivot.columns]
nrows, ncols = data.shape

non_zero = data[data > 0]
vmax = 1000 if len(non_zero) > 0 else 1
bounds = [0, 50, 150, 300, 500, 1000]
norm = mcolors.BoundaryNorm(bounds, CMAP.N)

# ── 4. DIMENSÕES E FIGURA ────────────────────────────────────────────────────

# Aumentamos as margens para acomodar título e legenda corretamente
CELL_W = 1.1
CELL_H = 0.5
LEFT_PAD = 2.2
TOP_PAD = 3
BOT_PAD = 1.0
SCALE = 1.2

fig_w = LEFT_PAD + ncols * CELL_W + 0.5
fig_h = TOP_PAD + nrows * CELL_H + BOT_PAD

fig = plt.figure(figsize=(fig_w, fig_h), facecolor=BG)

# Eixo principal do Heatmap (calculado em frações da figura)
ax_x = LEFT_PAD / fig_w
ax_y = BOT_PAD / fig_h
ax_w = (ncols * CELL_W) / fig_w
ax_h = (nrows * CELL_H) / fig_h

ax = fig.add_axes([ax_x, ax_y, ax_w, ax_h])
ax.set_facecolor(BG)

# ── 5. DESENHA AS CÉLULAS ────────────────────────────────────────────────────

for r in range(nrows):
    for c in range(ncols):
        val = data[r, c]
        if val == 0:
            face_color = ZERO_CLR
            txt_color = TXT_MID
        else:
            face_color = CMAP(norm(val))
            # Cálculo de luminância para contraste dinâmico
            luminance = (
                0.2126 * face_color[0] + 0.7152 * face_color[1] + 0.0722 * face_color[2])
            txt_color = TXT_LIGHT if luminance < 0.5 else TXT_DARK

        rect = plt.Rectangle((c, nrows - 1 - r), 1, 1,
                             facecolor=face_color, edgecolor=BG, linewidth=1.5)
        ax.add_patch(rect)

        label = str(int(val))
        ax.text(c + 0.5, nrows - 1 - r + 0.5, label, ha="center", va="center",
                fontsize=14 * SCALE, fontweight="600", color=txt_color, fontfamily=FONT)

# ── 6. EIXOS ─────────────────────────────────────────────────────────────────

ax.set_xlim(0, ncols)
ax.set_ylim(0, nrows)

# Colunas (anos da sentença) — no topo
ax.set_xticks(np.arange(ncols) + 0.5)
ax.set_xticklabels(cols, fontsize=16 * SCALE, fontweight="600",
                   color=TXT_DARK, fontfamily=FONT)
ax.xaxis.tick_top()
ax.plot(
    [-0.1, 1],   # começa no texto e vai até o final do eixo
    [1.0, 1.0],  # altura (topo)
    transform=ax.transAxes,
    color="black",
    linewidth=1.3,
    clip_on=False
)
ax.xaxis.set_label_position("top")
ax.tick_params(axis="x", length=0, pad=6)

# Linhas (Abertura) — com texto de 2 linhas
ax.set_yticks(np.arange(nrows) + 0.5)
ax.set_yticklabels(rows[::-1], fontsize=12 * SCALE, color=TXT_DARK,
                   va="center", multialignment="center",
                   fontfamily=FONT)
ax.tick_params(axis="y", length=1.2, pad=10)

for spine in ax.spines.values():
    spine.set_visible(False)

# ── 7. RÓTULO "Ano da Sentença" posicionado sobre a coluna "Abertura em" ─────
# Ancoramos em coordenadas do eixo: x=-0.001 = borda esquerda da grade,
# y=1.045 = levemente acima do topo, onde ficam os rótulos de coluna.
ax.text(
    -0.05, 1.01,
    "Ano da\nSentença",
    transform=ax.transAxes,
    fontsize=12 * SCALE, fontweight="800",
    color=TXT_DARK, fontfamily=FONT,
    ha="center", va="bottom",
    multialignment="center",
)

# ── 8. TÍTULO E LEGENDA DA COLOR BAR ─────────────────────────────────────────

title_y = 0.84

# Linha decorativa BBC (azul) acima do título
line_ax = fig.add_axes([LEFT_PAD / fig_w, title_y + 0.118, 0.40, 0.004])
line_ax.set_facecolor(ACCENT)
line_ax.axis("off")

# 2. Título Principal
title_text = "Ano de divulgação de sentenças procedentes e homologações\nconforme ano de abertura do processo"
fig.text(ax_x, 1 - (0.8 / fig_h), title_text,
         fontsize=16 * SCALE, fontweight="800", color=TXT_DARK, fontfamily=FONT,
         ha="left", va="top", linespacing=1.3)

# Color bar logo abaixo do título (no lugar do subtítulo de texto)
# 3. Legenda (Colorbar) - Abaixo do título
cb_w_norm = (ncols * CELL_W * 0.35) / fig_w
cb_ax = fig.add_axes([ax_x, 1 - (2.2 / fig_h), cb_w_norm, 0.025])
sm = plt.cm.ScalarMappable(cmap=CMAP, norm=norm)
sm.set_array([])
cb = plt.colorbar(sm, cax=cb_ax, orientation="horizontal")
cb.outline.set_visible(False)
cb.ax.tick_params(labelsize=11.5 * SCALE, length=0, pad=5)
cb.ax.set_title("Sentenças", fontsize=12 * SCALE, color=TXT_MID,
                loc='left', pad=10, fontfamily=FONT)

cb.set_ticks(bounds)
cb.set_ticklabels([str(b) for b in bounds])
for lbl in cb.ax.get_xticklabels():
    lbl.set_color(TXT_MID)
    lbl.set_fontfamily(FONT)


# ── 9. AJUSTE PARA FORMATO DE SLIDE (16:9) ───────────────────────────────────

# Dimensão padrão de slide (em polegadas)
SLIDE_W = 13.33   # largura (equivalente a 1920px)
SLIDE_H = 7.5     # altura  (equivalente a 1080px)

fig.set_size_inches(SLIDE_W, SLIDE_H)

# Recalcula posições mantendo proporção
ax.set_position([
    LEFT_PAD / SLIDE_W,
    BOT_PAD / SLIDE_H,
    (ncols * CELL_W) / SLIDE_W,
    (nrows * CELL_H) / SLIDE_H
])


# ── 10. SALVA E EXIBE ─────────────────────────────────────────────────────────

out_png = "heatmap_final.png"
plt.savefig(out_png, dpi=600, facecolor=BG)
print(f"✓ PNG salvo em: {out_png}")

plt.show()
