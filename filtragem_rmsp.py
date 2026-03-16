# %%

# Instalação das dependências necessárias para execução do script.
# %pip install pandas
# %pip install geopandas
# %pip install matplotlib
# %pip install openpyxl
# %pip install pathlib

# %%

# Importação das bibliotecas utilizadas no script:
# - geopandas: manipulação e análise de dados geoespaciais (shapefiles, GeoPackages, etc.)
# - pandas: manipulação de dados tabulares (DataFrames)
# - matplotlib: geração de gráficos e visualizações estáticas

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from pathlib import Path
from matplotlib import font_manager

# %%

# Caminhos de entrada e saída dos arquivos, relativos à raiz do projeto.
# Para executar o script, os arquivos devem estar organizados da seguinte forma:
# condominios_rmsp/
# ├── filtragem_rmsp.py
# ├── output/
# │   ├── TJSP_UTAS_RMSP.csv
# │   ├── grafico_sentencas_rmsP.png
#
# Define a pasta raiz do projeto como o diretório onde o script está localizado
BASE_DIR = Path(__file__).parent

# Caminhos relativos a partir da raiz do projeto
CSV_PATH = BASE_DIR / "output" / "TJSP_UTAS_RMSP.csv"
OUTPUT_PNG = BASE_DIR / "output" / "grafico_sentencas_rmsP.png"


# %%

# Leitura do arquivo CSV contendo os dados de condomínios raspados no Porta.
# <https://github.com/labcidade/portas>
# Termo da pesquisa no Porta:
# <condomin* E execuç* E (taxa OU quota OU cota OU despesa OU encargo OU contribuição) E débi*>
# O separador utilizado é o pipe ("|"),
# conforme formato de exportação dos dados do Portas

df = pd.read_csv(
    CSV_PATH,
    sep=",")

# %%
# Verificação do número de registros .

len(df)

# %%

font_manager.findSystemFonts(fontpaths=None, fontext='ttf')

# %%

mpl.rcParams.update({

    # Fonte global
    "font.family": "Fira Sans",
    "font.size": 12,

    # Estilo dos eixos
    "axes.linewidth": 1.2,
    "axes.edgecolor": "black",

    # Remover grade padrão
    "axes.grid": False,

    # Ticks
    "xtick.direction": "out",
    "ytick.direction": "out",

    # Remover bordas superiores
    "axes.spines.top": False,
    "axes.spines.right": False
})

# %%
# Contagem do número de processos por ano
contagem_anos = (
    df[(df['Ano etiqueta'] >= 2008) &
       (df['Ano etiqueta'] <= 2024)]
    ['Ano etiqueta']
    .astype(int)                      # garante anos inteiros
    .value_counts()
    .sort_index()
)

plt.figure(figsize=(10, 5))

# Título principal
plt.suptitle(
    "Evolução Anual das Sentenças em Ações Condominiais por Inadimplência",
    fontsize=16,
    fontweight="bold",
    ha="center"
)

# Subtítulo
plt.title(
    "Região Metropolitana de São Paulo (2006 - 2024)",
    fontsize=14,
    loc="center"
)

# Barras
barras = plt.bar(
    contagem_anos.index,
    contagem_anos.values,
    color="#1F77B4",   # azul estilo BBC
    edgecolor="none"
)

# Valores nas barras
for barra in barras:
    altura = barra.get_height()
    plt.text(
        barra.get_x() + barra.get_width()/2,
        altura * 0.5,
        f'{int(altura):,}'.replace(",", "."),
        ha="center",
        va="center",
        color="white",
        fontweight="bold",
        rotation=90,
        fontsize=14
    )

# Eixo Y
plt.ylabel("Número de Sentenças", fontsize=14, fontweight="bold")

max_valor = contagem_anos.max()
ticks = range(0, max_valor + 500, 500)
plt.yticks(ticks, fontsize=14)

# Remover rótulo eixo X
plt.xlabel("")

# Anos verticais
plt.xticks(contagem_anos.index.astype(int), rotation=90, fontsize=14)

# Ticks do eixo Y
plt.yticks(fontsize=14)

plt.tight_layout()

# Salvar o gráfico no diretório output
plt.savefig(
    OUTPUT_PNG,
    dpi=300,
    bbox_inches="tight"
)

plt.show()
# %%
