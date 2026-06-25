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
from pathlib import Path

# %%

# Caminhos de entrada e saída dos arquivos, relativos à raiz do projeto.
# Para executar o script, os arquivos devem estar organizados da seguinte forma:
#   condominios_rmsp/
#   ├── condominios_rmsp.py
#   ├── data/
#   │   ├── Condominios_resultados.csv
#   │   └── shapefiles/
#   │       ├── PORTAS_TJSP_UTAS.shp (+ .dbf, .prj, .shx)
#   │       └── GeoSampa_LimitesAdministrativos_RMSP-MSP.gpkg
#   └── output/

# Define a pasta raiz do projeto como o diretório onde o script está localizado
BASE_DIR = Path.cwd()

# Caminhos relativos a partir da raiz do projeto
CSV_PATH = BASE_DIR / "data" / "Condominios_resultados.csv"
SHP_UTAS_PATH = BASE_DIR / "data" / "shapefiles" / "PORTAS_TJSP_UTAS.shp"
GPKG_RMSP_PATH = BASE_DIR / "data" / "shapefiles" / \
    "GeoSampa_LimitesAdministrativos_RMSP-MSP.gpkg"
OUTPUT_XLSX = BASE_DIR / "output" / "TJSP_UTAS_RMSP.xlsx"
OUTPUT_CSV = BASE_DIR / "output" / "TJSP_UTAS_RMSP.csv"
OUTPUT_SHP = BASE_DIR / "data" / "shapefiles" / "UTA_RMSP.shp"


# %%

# Leitura do arquivo CSV contendo os dados de condomínios raspados no Porta.
# <https://github.com/labcidade/portas>
# Termo da pesquisa no Porta:
# <condomin* E execuç* E (taxa OU quota OU cota OU despesa OU encargo OU contribuição) E débi*>
# O separador utilizado é o pipe ("|"),
# conforme formato de exportação dos dados do Portas

df = pd.read_csv(
    CSV_PATH,
    sep="|")

# %%

# Verificação da estrutura do csv.
# Contagem do número total de registros (linhas) na tabela bruta.
# df.head()

len(df)

# %%
# Verificação de processos duplicados na coluna 'Processo'
duplicados = df[df.duplicated(subset='Processo', keep=False)]

print(f"Total de processos repetidos: {duplicados['Processo'].nunique()}")
print(f"Total de linhas com repetição: {len(duplicados)}")
print(duplicados[['Processo']].value_counts())

# %%

# Remoção de linhas com processos duplicados,
# mantendo apenas a primeira ocorrência de cada processo
# Isso é importante, pois pelo padrão CNJ só há um código de processo único.
df = df.drop_duplicates(subset='Processo', keep='first')
len(df)

# %%

# Filtragem dos registros por Região Administrativa de Justiça (RAJ).
# São mantidos apenas os RAJ do qual estão presentes os
# municípios da Região Metropolitana de São Paulo (RMSP) - são eles:
# Grande São Paulo, Campinas, São José dos Campos e Santos.

desp_cond = df[(df['RAJ'] == '1ª RAJ - Grande São Paulo') |
               (df['RAJ'] == '4ª RAJ – Campinas') |
               (df['RAJ'] == '9ª RAJ - SJ dos Campos') |
               (df['RAJ'] == '7ª RAJ – Santos')]


# %%

# Verificação do número de registros após a filtragem por RAJ.

len(desp_cond)

# %%
# Leitura dos arquivos vetoriais geoespaciais:
# - TJSP_UTAS: shapefile com os polígonos das Unidades Territoriais de Atendimento do TJSP.
# - RMSP: camada GeoPackage com os limites administrativos da Região Metropolitana de São Paulo,
#   originária do portal GeoSampa.
# Ambos os arquivos estão presentes ou na base de dados do LabCidade no GitHub junto com este script

TJSP_UTAS = gpd.read_file(
    SHP_UTAS_PATH)

RMSP = gpd.read_file(
    GPKG_RMSP_PATH,
    layer='GeoSampa_RMSP')

# %%
# Verificação dos Sistemas de Referência de Coordenadas (CRS) originais de cada camada.
# É fundamental garantir que ambas as camadas estejam no mesmo CRS antes de operações espaciais.
# Padrão do Brasil para dados geoespaciais é o SIRGAS 2000, código EPSG 4674 para geográfico e 31983 para projetado (UTM fuso 23S).

print(TJSP_UTAS.crs)
print(RMSP.crs)

# %%
# Atribuição do CRS SIRGAS 2000 / UTM zona 23S (EPSG:31983) à camada TJSP_UTAS,
# caso ela não possua um CRS definido. Isso evita erros em reprojeções e operações espaciais

if TJSP_UTAS.crs is None:
    TJSP_UTAS = TJSP_UTAS.set_crs(31983)

# %%
# Reprojeção de ambas as camadas para o SIRGAS 2000 geográfico (EPSG:4674),
# garantindo que estejam no mesmo CRS para operações de sobreposição espacial.

TJSP_UTAS = TJSP_UTAS.to_crs(4674)
RMSP = RMSP.to_crs(4674)

# %%

# Visualização: plotagem da RMSP como camada base e das UTAs do TJSP sobrepostas,
# para confirmar o alinhamento espacial entre as duas camadas após a reprojeção.

SP_RMSP = RMSP.plot(figsize=(6, 6))
TJSP_UTAS.plot(ax=SP_RMSP, color="red", markersize=5)

# %%

# Padronização dos campos de chave de junção:
# - 'COD_UTA' em TJSP_UTAS e 'UTA' em desp_cond são convertidos para string
#   e têm espaços extras removidos (strip), evitando falhas na junção por diferenças de formatação.

TJSP_UTAS['COD_UTA'] = TJSP_UTAS['COD_UTA'].astype(str).str.strip()
desp_cond['UTA'] = desp_cond['UTA'].astype(str).str.strip()


# %%
# Junção (merge) tabular entre a camada geoespacial TJSP_UTAS e a tabela de condomínios filtrada.
# A junção é feita pela correspondência entre 'COD_UTA' (shapefile) e 'UTA' (tabela CSV).
# O tipo 'left' preserva todas as linhas de TJSP_UTAS, mesmo sem correspondência na tabela.

TJSP_UTAS_Join = TJSP_UTAS.merge(
    desp_cond,
    left_on='COD_UTA',
    right_on='UTA',
    how='left'
)

# %%
# Visualização da camada resultante do merge para inspeção visual preliminar.

TJSP_UTAS_Join.plot()

# %%
# Junção espacial (spatial join) entre as UTAs com dados de condomínios e os limites da RMSP.
# Mantém apenas as UTAs que intersectam geometricamente os municípios da RMSP (how="inner").

UTA_RMSP = gpd.sjoin(TJSP_UTAS_Join, RMSP, how="inner", predicate="intersects")

# %%
# Lista de códigos de UTAs a serem excluídos manualmente do resultado.
# Esses códigos correspondem a unidades identificadas como fora do escopo
# de análise ou com inconsistências geoespaciais após verificação.

codigos_excluir = [
    "07C07", "10C22", "07C08", "10C05", "07C18", "01C22", "10C07", "07C03",
    "04C29", "09C13", "09C06", "04C37", "07C11", "07C17", "09C19", "04C07",
    "04C13", "09C11", "07C01", "09C23"
]
UTA_RMSP = UTA_RMSP[~UTA_RMSP['COD_UTA'].isin(codigos_excluir)]

# %%
# Verificação do número de UTAs restantes após a exclusão manual.

len(UTA_RMSP)

# %%
# Remoção da coluna 'geometry' da camada UTA_RMSP,
# convertendo-a em um DataFrame tabular comum (sem geometria) para exportação em formato Excel.

df_uta = UTA_RMSP.drop(columns="geometry")

# %%

# Exportação do DataFrame tabular (sem geometria) para um arquivo Excel (.xlsx).
# O parâmetro index=False evita a inclusão do índice do DataFrame como coluna na planilha.

df_uta.to_excel(OUTPUT_XLSX,
                index=False)
df_uta.to_csv(OUTPUT_CSV,
              index=False)

# %%
# Exportação da camada geoespacial resultante (UTAs da RMSP com dados de condomínios)
# para um novo shapefile no formato ESRI Shapefile.

UTA_RMSP.to_file(OUTPUT_SHP,
                 driver="ESRI Shapefile")
