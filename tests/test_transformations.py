import pandas as pd
import pytest

from src.transformations import ibge_localidades as ibge_module
from src.transformations import sinisa as sinisa_module
from src.utils.cleaning import (
    apply_geography_standardization,
    infer_numeric_columns,
    normalize_nulls,
    standardize_codigo_ibge,
    standardize_uf,
)


def test_standardize_codigo_ibge():
    series = pd.Series(["3550308", "3550308.0", " 3304557 ", "123", None])
    result = standardize_codigo_ibge(series)

    assert result.iloc[0] == 3550308
    assert result.iloc[1] == 3550308
    assert result.iloc[2] == 3304557
    assert pd.isna(result.iloc[3])
    assert pd.isna(result.iloc[4])


def test_standardize_uf():
    series = pd.Series(["sp", " SP ", "XX", None])
    result = standardize_uf(series)

    assert result.iloc[0] == "SP"
    assert result.iloc[1] == "SP"
    assert pd.isna(result.iloc[2])
    assert pd.isna(result.iloc[3])


def test_normalize_nulls():
    df = pd.DataFrame(
        {
            "municipio": ["São Paulo", "NA", "-", "  "],
            "valor": ["10", "N/A", "5", "null"],
        }
    )
    cleaned = normalize_nulls(df)

    assert cleaned.iloc[0]["municipio"] == "São Paulo"
    assert pd.isna(cleaned.iloc[1]["municipio"])
    assert pd.isna(cleaned.iloc[2]["municipio"])
    assert pd.isna(cleaned.iloc[3]["valor"])


def test_apply_geography_standardization():
    df = pd.DataFrame(
        {
            "codigo_ibge": ["3550308.0", "3304557"],
            "uf": ["sp", "rj"],
            "municipio": ["  São Paulo  ", "Rio de Janeiro"],
        }
    )
    result = apply_geography_standardization(df)

    assert result.iloc[0]["codigo_ibge"] == 3550308
    assert result.iloc[0]["uf"] == "SP"
    assert result.iloc[0]["municipio"] == "São Paulo"


def test_infer_numeric_columns():
    df = pd.DataFrame(
        {
            "ano": ["2022", "2023", "2024"],
            "taxa": ["95.5", "88.1", "N/A"],
            "municipio": ["A", "B", "C"],
        }
    )
    cleaned = normalize_nulls(df)
    result = infer_numeric_columns(cleaned)

    assert result["ano"].dtype.name == "Int64"
    assert result["taxa"].dtype.name == "Float64"
    assert result["municipio"].dtype == object


@pytest.fixture
def sample_ibge_municipios():
    return pd.DataFrame(
        {
            "id_municipio": [3550308, 3304557],
            "nome_municipio": ["  São Paulo ", "Rio de Janeiro"],
            "id_microrregiao": [35061, 33018],
            "nome_microrregiao": ["São Paulo", "Rio de Janeiro"],
            "id_mesorregiao": [3515, 3306],
            "nome_mesorregiao": ["Metropolitana de São Paulo", "Metropolitana do Rio de Janeiro"],
            "id_estado": [35, 33],
            "sigla_estado": ["sp", "RJ"],
            "nome_estado": ["São Paulo", "Rio de Janeiro"],
            "id_regiao": [3, 3],
            "sigla_regiao": ["se", "SE"],
            "nome_regiao": ["Sudeste", "Sudeste"],
            "id_regiao_imediata": [350001, 330001],
            "nome_regiao_imediata": ["São Paulo", "Rio de Janeiro"],
            "id_regiao_intermediaria": [3501, 3301],
            "nome_regiao_intermediaria": ["São Paulo", "Rio de Janeiro"],
            "fonte": ["IBGE - API Localidades", "IBGE - API Localidades"],
            "dt_ingestao": pd.to_datetime(["2026-01-01", "2026-01-01"], utc=True),
        }
    )


def test_transform_municipios(sample_ibge_municipios):
    result = ibge_module.transform_municipios(sample_ibge_municipios)

    assert result.iloc[0]["codigo_ibge"] == 3550308
    assert result.iloc[0]["sigla_uf"] == "SP"
    assert result.iloc[0]["nome_municipio"] == "São Paulo"
    assert "dt_transformacao" in result.columns


def test_transform_ibge_localidades(tmp_path, sample_ibge_municipios):
    bronze_dir = tmp_path / "bronze"
    silver_dir = tmp_path / "silver"
    bronze_dir.mkdir()

    sample_ibge_municipios.to_parquet(bronze_dir / "ibge_municipios.parquet", index=False)

    paths = ibge_module.transform_ibge_localidades(
        input_dir=bronze_dir,
        output_dir=silver_dir,
    )

    assert "municipios" in paths
    silver = pd.read_parquet(paths["municipios"])
    assert len(silver) == 2
    assert silver.iloc[0]["sigla_estado"] == "SP"


def test_transform_sinisa(tmp_path):
    bronze_dir = tmp_path / "bronze"
    silver_dir = tmp_path / "silver"
    bronze_dir.mkdir()

    bronze_df = pd.DataFrame(
        {
            "codigo_ibge": ["3550308.0", "3304557"],
            "municipio": ["  São Paulo ", "Rio de Janeiro"],
            "uf": ["sp", "rj"],
            "ano": ["2022", "2023"],
            "populacao_atendida": ["95.5", "N/A"],
            "fonte": ["SINISA - SNIS", "SINISA - SNIS"],
            "arquivo_origem": ["prestadores.csv", "prestadores.csv"],
            "dt_ingestao": pd.to_datetime(["2026-01-01", "2026-01-01"], utc=True),
        }
    )
    bronze_df.to_parquet(bronze_dir / "sinisa_prestadores.parquet", index=False)

    paths = sinisa_module.transform_sinisa(input_dir=bronze_dir, output_dir=silver_dir)

    assert "prestadores" in paths
    silver = pd.read_parquet(paths["prestadores"])
    assert silver.iloc[0]["codigo_ibge"] == 3550308
    assert silver.iloc[0]["uf"] == "SP"
    assert silver["ano"].dtype.name == "Int64"
    assert pd.isna(silver.iloc[1]["populacao_atendida"])
