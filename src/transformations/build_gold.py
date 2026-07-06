from pathlib import Path
import logging
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

IBGE_MUNICIPIOS_PATH = PROJECT_ROOT / "data" / "silver" / "ibge_municipios.parquet"
SINISA_AGUA_PATH = PROJECT_ROOT / "data" / "silver" / "sinisa" / "sinisa_indicadores_abastecimento_agua.parquet"
GOLD_DIR = PROJECT_ROOT / "data" / "gold"
OUTPUT_PATH = GOLD_DIR / "infra_municipios_agua.parquet"


def find_column(df: pd.DataFrame, candidates: list[str]) -> str:
    for col in candidates:
        if col in df.columns:
            return col

    raise ValueError(
        f"Nenhuma coluna encontrada entre as opções: {candidates}. "
        f"Colunas disponíveis: {df.columns.tolist()}"
    )


def to_numeric_br(value):
    """
    Converte números brasileiros em texto para float.
    Exemplo: '60,35' -> 60.35
    Valores como 'Não calculado' viram nulo.
    """
    if pd.isna(value):
        return pd.NA

    value = str(value).strip()

    if value == "":
        return pd.NA

    invalid_values = [
        "nao calculado",
        "não calculado",
        "nan",
        "none",
        "-",
    ]

    if value.lower() in invalid_values or "não calculado" in value.lower() or "nao calculado" in value.lower():
        return pd.NA

    value = value.replace(".", "").replace(",", ".")

    try:
        return float(value)
    except ValueError:
        return pd.NA


def build_gold_infra_municipios_agua() -> Path:
    logger.info("Lendo dados Silver do IBGE: %s", IBGE_MUNICIPIOS_PATH)
    ibge = pd.read_parquet(IBGE_MUNICIPIOS_PATH)

    logger.info("Lendo dados Silver do SINISA Água: %s", SINISA_AGUA_PATH)
    sinisa = pd.read_parquet(SINISA_AGUA_PATH)

    ibge_codigo_col = find_column(
        ibge,
        ["id", "codigo_ibge", "cod_ibge", "codigo_municipio", "municipio_id"],
    )

    sinisa_codigo_col = find_column(
        sinisa,
        ["cod_ibge", "codigo_ibge", "codigo_do_ibge"],
    )

    logger.info("Coluna de município IBGE: %s", ibge_codigo_col)
    logger.info("Coluna de município SINISA: %s", sinisa_codigo_col)

    ibge = ibge.copy()
    sinisa = sinisa.copy()

    ibge["codigo_ibge"] = ibge[ibge_codigo_col].astype(str).str.strip()
    sinisa["codigo_ibge"] = sinisa[sinisa_codigo_col].astype(str).str.strip()

    # Seleciona colunas principais do SINISA
    sinisa_cols = [
        "codigo_ibge",
        "macrorregiao",
        "municipio",
        "uf",
        "capital",
        "rm_ride",
        "natureza_juridica",
        "abrangencia",
        "nome_do_prestador",
        "sigla",
        "iag0001",
        "iag0002",
        "iag0003",
        "iag0004",
        "iag0005",
        "iag0006",
        "fonte",
        "arquivo_origem",
        "dt_ingestao",
    ]

    sinisa_cols = [col for col in sinisa_cols if col in sinisa.columns]
    sinisa_gold = sinisa[sinisa_cols].copy()

    # Converte indicadores numéricos
    for col in ["iag0001", "iag0002", "iag0003", "iag0004", "iag0005", "iag0006"]:
        if col in sinisa_gold.columns:
            sinisa_gold[col] = sinisa_gold[col].apply(to_numeric_br)

    # Seleciona algumas colunas úteis do IBGE, se existirem
    ibge_cols = [
        "codigo_ibge",
        "nome",
        "microrregiao_id",
        "microrregiao_nome",
        "mesorregiao_id",
        "mesorregiao_nome",
        "uf_id",
        "uf_sigla",
        "uf_nome",
        "regiao_id",
        "regiao_sigla",
        "regiao_nome",
    ]

    ibge_cols = [col for col in ibge_cols if col in ibge.columns]
    ibge_gold = ibge[ibge_cols].drop_duplicates(subset=["codigo_ibge"])

    gold = sinisa_gold.merge(
        ibge_gold,
        on="codigo_ibge",
        how="left",
        suffixes=("_sinisa", "_ibge"),
    )

    gold["ano_referencia"] = 2024

    GOLD_DIR.mkdir(parents=True, exist_ok=True)

    gold.to_parquet(OUTPUT_PATH, index=False)

    logger.info(
        "Gold salvo em %s (%s registros, %s colunas)",
        OUTPUT_PATH,
        len(gold),
        len(gold.columns),
    )

    return OUTPUT_PATH


def main() -> None:
    path = build_gold_infra_municipios_agua()
    print(f"Tabela Gold criada: {path}")


if __name__ == "__main__":
    main()