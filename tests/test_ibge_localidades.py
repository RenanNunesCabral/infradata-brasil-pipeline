from pathlib import Path

import pandas as pd
import pytest

from src.ingestion import ibge_localidades as module


@pytest.fixture
def sample_regioes():
    return [{"id": 1, "sigla": "N", "nome": "Norte"}]


@pytest.fixture
def sample_estados():
    return [
        {
            "id": 35,
            "sigla": "SP",
            "nome": "São Paulo",
            "regiao": {"id": 3, "sigla": "SE", "nome": "Sudeste"},
        }
    ]


@pytest.fixture
def sample_municipios():
    return [
        {
            "id": 3550308,
            "nome": "São Paulo",
            "microrregiao": {
                "id": 35061,
                "nome": "São Paulo",
                "mesorregiao": {
                    "id": 3515,
                    "nome": "Metropolitana de São Paulo",
                    "UF": {
                        "id": 35,
                        "sigla": "SP",
                        "nome": "São Paulo",
                        "regiao": {"id": 3, "sigla": "SE", "nome": "Sudeste"},
                    },
                },
            },
            "regiao-imediata": {
                "id": 350001,
                "nome": "São Paulo",
                "regiao-intermediaria": {
                    "id": 3501,
                    "nome": "São Paulo",
                    "UF": {
                        "id": 35,
                        "sigla": "SP",
                        "nome": "São Paulo",
                        "regiao": {"id": 3, "sigla": "SE", "nome": "Sudeste"},
                    },
                },
            },
        }
    ]


def test_normalize_regioes(sample_regioes):
    df = module.normalize_regioes(sample_regioes)

    assert list(df.columns) == [
        "id_regiao",
        "sigla_regiao",
        "nome_regiao",
        "fonte",
        "dt_ingestao",
    ]
    assert df.iloc[0]["id_regiao"] == 1
    assert df.iloc[0]["sigla_regiao"] == "N"
    assert df.iloc[0]["fonte"] == module.FONTE


def test_normalize_estados(sample_estados):
    df = module.normalize_estados(sample_estados)

    assert df.iloc[0]["id_estado"] == 35
    assert df.iloc[0]["sigla_estado"] == "SP"
    assert df.iloc[0]["nome_regiao"] == "Sudeste"


def test_normalize_municipios(sample_municipios):
    df = module.normalize_municipios(sample_municipios)

    assert df.iloc[0]["id_municipio"] == 3550308
    assert df.iloc[0]["sigla_estado"] == "SP"
    assert df.iloc[0]["nome_regiao_intermediaria"] == "São Paulo"


def test_normalize_municipios_sem_microrregiao():
    records = [
        {
            "id": 5101837,
            "nome": "Boa Esperança do Norte",
            "microrregiao": None,
            "regiao-imediata": {
                "id": 510008,
                "nome": "Sorriso",
                "regiao-intermediaria": {
                    "id": 5103,
                    "nome": "Sinop",
                    "UF": {
                        "id": 51,
                        "sigla": "MT",
                        "nome": "Mato Grosso",
                        "regiao": {"id": 5, "sigla": "CO", "nome": "Centro-Oeste"},
                    },
                },
            },
        }
    ]

    df = module.normalize_municipios(records)

    assert pd.isna(df.iloc[0]["id_microrregiao"])
    assert df.iloc[0]["sigla_estado"] == "MT"


def test_ingest_localidades(tmp_path, monkeypatch, sample_regioes, sample_estados, sample_municipios):
    def fake_fetch(endpoint: str):
        payloads = {
            "regioes": sample_regioes,
            "estados": sample_estados,
            "municipios": sample_municipios,
        }
        return payloads[endpoint]

    monkeypatch.setattr(module, "_fetch", fake_fetch)

    paths = module.ingest_localidades(output_dir=tmp_path)

    assert paths["regioes"].exists()
    assert paths["estados"].exists()
    assert paths["municipios"].exists()

    regioes = pd.read_parquet(paths["regioes"])
    assert len(regioes) == 1
