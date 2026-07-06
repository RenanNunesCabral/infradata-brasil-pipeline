from pathlib import Path

import pandas as pd


def save_parquet(df: pd.DataFrame, path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    df = df.copy()

    # Evita erro do pyarrow com colunas object misturando texto, número e vazio
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype("string")

    df.to_parquet(path, index=False, engine="pyarrow")
