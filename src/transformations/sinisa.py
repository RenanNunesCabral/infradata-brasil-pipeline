"""
Transformação dos dados SINISA da camada bronze para silver.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from src.utils.cleaning import (
    apply_geography_standardization,
    infer_numeric_columns,
    normalize_nulls,
    transformation_timestamp,
)
from src.utils.io import save_parquet
from src.utils.paths import SINISA_BRONZE_DIR, SINISA_SILVER_DIR

logger = logging.getLogger(__name__)


def transform_sinisa_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = normalize_nulls(df)
    cleaned = apply_geography_standardization(cleaned)
    cleaned = infer_numeric_columns(cleaned)
    cleaned["dt_transformacao"] = transformation_timestamp()
    return cleaned


def transform_sinisa(
    input_dir: Path | None = None,
    output_dir: Path | None = None,
) -> dict[str, Path]:
    source_dir = input_dir or SINISA_BRONZE_DIR
    target_dir = output_dir or SINISA_SILVER_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    if not source_dir.exists():
        logger.warning("Pasta bronze SINISA não encontrada: %s", source_dir)
        return {}

    bronze_files = sorted(source_dir.glob("sinisa_*.parquet"))
    if not bronze_files:
        logger.warning("Nenhum arquivo bronze SINISA encontrado em %s", source_dir)
        return {}

    saved_paths: dict[str, Path] = {}
    for source_path in bronze_files:
        logger.info("Transformando %s...", source_path.name)
        bronze_df = pd.read_parquet(source_path)
        silver_df = transform_sinisa_dataframe(bronze_df)
        output_path = save_parquet(silver_df, target_dir / source_path.name)
        saved_paths[source_path.stem.removeprefix("sinisa_") or source_path.stem] = output_path
        logger.info(
            "Silver salvo: %s (%s registros, %s colunas)",
            output_path,
            len(silver_df),
            len(silver_df.columns),
        )

    return saved_paths
