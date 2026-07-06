from pathlib import Path

import pandas as pd
import pytest

from src.ingestion import sinisa as module
from src.utils.columns import standardize_column_name, standardize_column_names


def test_standardize_column_name():
    assert standardize_column_name("  Código IBGE  ") == "codigo_ibge"
    assert standardize_column_name("Ano de Referência") == "ano_de_referencia"
    assert standardize_column_name("População Atendida (%)") == "populacao_atendida"


def test_standardize_column_names_handles_duplicates():
    assert standardize_column_names(["Ano", "Ano", "Ano"]) == ["ano", "ano_2", "ano_3"]


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    path = tmp_path / "prestadores.csv"
    path.write_text(
        "Código IBGE,Município,Ano,População Atendida (%)\n"
        "3550308,São Paulo,2022,95.5\n"
        "3304557,Rio de Janeiro,2022,88.1\n",
        encoding="utf-8",
    )
    return path


def test_read_and_normalize_csv(sample_csv: Path):
    df = module.read_file(sample_csv)
    normalized = module.normalize_dataframe(df, sample_csv)

    assert list(normalized.columns[:4]) == [
        "codigo_ibge",
        "municipio",
        "ano",
        "populacao_atendida",
    ]
    assert normalized.iloc[0]["codigo_ibge"] == 3550308
    assert normalized.iloc[0]["fonte"] == module.FONTE
    assert normalized.iloc[0]["arquivo_origem"] == sample_csv.name


def test_ingest_sinisa(tmp_path: Path, sample_csv: Path):
    input_dir = tmp_path / "raw"
    output_dir = tmp_path / "bronze"
    input_dir.mkdir()
    output_dir.mkdir()

    target_csv = input_dir / sample_csv.name
    target_csv.write_text(sample_csv.read_text(encoding="utf-8"), encoding="utf-8")

    paths = module.ingest_sinisa(input_dir=input_dir, output_dir=output_dir)

    assert len(paths) == 1
    output_path = paths["prestadores"]
    assert output_path.exists()

    result = pd.read_parquet(output_path)
    assert len(result) == 2
    assert "dt_ingestao" in result.columns


def test_ingest_sinisa_empty_directory(tmp_path: Path, caplog):
    caplog.set_level("WARNING")
    paths = module.ingest_sinisa(input_dir=tmp_path / "vazio", output_dir=tmp_path / "bronze")
    assert paths == {}
