from pathlib import Path
import sys

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Garante que o Streamlit consiga importar módulos da pasta src
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.utils.sinisa_labels import SINISA_AGUA_LABELS


GOLD_PATH = PROJECT_ROOT / "data" / "gold" / "infra_municipios_agua.parquet"


st.set_page_config(
    page_title="InfraData Brasil",
    page_icon="💧",
    layout="wide",
)


COLUMN_LABELS = {
    "codigo_ibge": "Código IBGE",
    "municipio": "Município",
    "uf": "UF",
    "nome_do_prestador": "Nome do prestador",
    "natureza_juridica": "Natureza jurídica",
    "abrangencia": "Abrangência",
    "capital": "Capital",
    "rm_ride": "RM/RIDE",
    "fonte": "Fonte",
    "arquivo_origem": "Arquivo de origem",
    "dt_ingestao": "Data de ingestão",
    "ano_referencia": "Ano de referência",
    **SINISA_AGUA_LABELS,
}


def get_label(coluna: str) -> str:
    return COLUMN_LABELS.get(coluna, coluna)


def rename_columns_for_display(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns=COLUMN_LABELS)


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_parquet(GOLD_PATH)


def format_percent(value):
    if pd.isna(value):
        return "-"
    return f"{value:.2f}%"


df = load_data()

st.title("💧 InfraData Brasil")

st.markdown(
    """
    Pipeline de engenharia de dados para integração e análise de dados públicos
    de infraestrutura brasileira, começando por indicadores de abastecimento de água do SINISA.
    """
)

st.sidebar.header("Filtros")

ufs = sorted(df["uf"].dropna().unique()) if "uf" in df.columns else []
uf_selected = st.sidebar.multiselect("UF", ufs, default=ufs)

filtered = df.copy()

if uf_selected and "uf" in filtered.columns:
    filtered = filtered[filtered["uf"].isin(uf_selected)]


indicadores_disponiveis = [
    col for col in SINISA_AGUA_LABELS.keys()
    if col in filtered.columns
]

if indicadores_disponiveis:
    indicador_selecionado = st.sidebar.selectbox(
        "Indicador de análise",
        indicadores_disponiveis,
        index=0,
        format_func=lambda col: get_label(col),
    )
else:
    indicador_selecionado = None


st.subheader("Visão Geral")

col1, col2, col3, col4 = st.columns(4)

total_municipios = (
    filtered["codigo_ibge"].nunique()
    if "codigo_ibge" in filtered.columns
    else len(filtered)
)

total_ufs = (
    filtered["uf"].nunique()
    if "uf" in filtered.columns
    else 0
)

media_atendimento_total = (
    pd.to_numeric(filtered["iag0001"], errors="coerce").mean()
    if "iag0001" in filtered.columns
    else None
)

media_indicador_selecionado = (
    pd.to_numeric(filtered[indicador_selecionado], errors="coerce").mean()
    if indicador_selecionado
    else None
)

col1.metric("Municípios analisados", f"{total_municipios:,}".replace(",", "."))
col2.metric("UFs analisadas", total_ufs)
col3.metric("Atendimento total de água", format_percent(media_atendimento_total))

if indicador_selecionado:
    col4.metric("Média do indicador selecionado", format_percent(media_indicador_selecionado))
else:
    col4.metric("Média do indicador selecionado", "-")


st.divider()


if indicador_selecionado:
    st.subheader(f"Ranking por indicador: {get_label(indicador_selecionado)}")

    ranking_cols = [
        col for col in [
            "codigo_ibge",
            "municipio",
            "uf",
            "nome_do_prestador",
            "natureza_juridica",
            indicador_selecionado,
        ]
        if col in filtered.columns
    ]

    ranking = filtered[ranking_cols].copy()
    ranking[indicador_selecionado] = pd.to_numeric(
        ranking[indicador_selecionado],
        errors="coerce",
    )

    ranking_menor = ranking.sort_values(
        indicador_selecionado,
        ascending=True,
        na_position="last",
    )

    ranking_maior = ranking.sort_values(
        indicador_selecionado,
        ascending=False,
        na_position="last",
    )

    st.markdown("### Municípios com menor valor no indicador")
    st.dataframe(
        rename_columns_for_display(ranking_menor.head(20)),
        use_container_width=True,
    )

    st.markdown("### Municípios com maior valor no indicador")
    st.dataframe(
        rename_columns_for_display(ranking_maior.head(20)),
        use_container_width=True,
    )
else:
    st.warning("Nenhum indicador SINISA foi encontrado na tabela Gold.")


st.divider()

st.subheader("Média do indicador por UF")

if indicador_selecionado and "uf" in filtered.columns:
    temp = filtered.copy()
    temp[indicador_selecionado] = pd.to_numeric(
        temp[indicador_selecionado],
        errors="coerce",
    )

    uf_summary = (
        temp.groupby("uf", as_index=False)
        .agg(
            media_indicador=(indicador_selecionado, "mean"),
            municipios=("codigo_ibge", "nunique"),
        )
        .sort_values("media_indicador", ascending=False)
    )

    uf_summary_display = uf_summary.rename(
        columns={
            "uf": "UF",
            "media_indicador": get_label(indicador_selecionado),
            "municipios": "Municípios",
        }
    )

    st.bar_chart(
        uf_summary.set_index("uf")["media_indicador"]
    )

    st.dataframe(uf_summary_display, use_container_width=True)


st.divider()

st.subheader("Distribuição por natureza jurídica do prestador")

if "natureza_juridica" in filtered.columns:
    natureza = (
        filtered["natureza_juridica"]
        .fillna("Não informado")
        .value_counts()
        .reset_index()
    )

    natureza.columns = ["natureza_juridica", "quantidade"]

    natureza_display = natureza.rename(
        columns={
            "natureza_juridica": "Natureza jurídica",
            "quantidade": "Quantidade",
        }
    )

    st.dataframe(natureza_display, use_container_width=True)

    st.bar_chart(
        natureza.set_index("natureza_juridica")["quantidade"]
    )


st.divider()

st.subheader("Base analítica Gold")

st.markdown(
    """
    A tabela abaixo mantém a estrutura da camada Gold, mas no dashboard os códigos dos indicadores
    são traduzidos para descrições amigáveis.
    """
)

display_df = rename_columns_for_display(filtered.copy())

st.dataframe(display_df, use_container_width=True)

st.download_button(
    label="Baixar dados filtrados em CSV",
    data=display_df.to_csv(index=False, sep=";").encode("utf-8-sig"),
    file_name="infradata_brasil_gold.csv",
    mime="text/csv",
)