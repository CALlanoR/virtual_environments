"""
Genera un PNG con paneles de las métricas de I/O capturadas por
monitor-mysql5.7.sh / monitor-mysql8.sh.

Uso:
  plot.py CSV1 [CSV2] [-o OUT.png] [--title TEXT] [--smooth N]

Cuando se pasan dos CSVs, los superpone en cada panel para comparar stacks.
La columna 'stack' del CSV se usa como label de la leyenda.
Se alinea por tiempo relativo desde la primera muestra de cada CSV.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

REQUIRED_COLUMNS = {
    "timestamp", "stack",
    "blkio_read_bps", "blkio_write_bps",
    "netio_tx_bps",
    "innodb_read_bps", "innodb_write_bps",
    "mysql_bytes_sent_bps",
}

PANELS = [
    ("blkio_read_bps",       "BlockIO read (B/s)"),
    ("blkio_write_bps",      "BlockIO write (B/s)"),
    ("innodb_read_bps",      "Innodb_data_read (B/s)"),
    ("innodb_write_bps",     "Innodb_data_written (B/s)"),
    ("mysql_bytes_sent_bps", "MySQL Bytes_sent (B/s)"),
    ("netio_tx_bps",         "NetIO tx (B/s)"),
]


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"CSV no encontrado: {path}")
    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"{path}: faltan columnas {sorted(missing)}")
    if df.empty:
        raise ValueError(f"{path}: CSV vacío")

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    if df["timestamp"].isna().all():
        raise ValueError(f"{path}: ninguna fila tiene timestamp parseable")

    # Convertir métricas a numérico; "baseline" y "?" se vuelven NaN.
    numeric_cols = [c for c, _ in PANELS]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Tiempo relativo (segundos desde la primera muestra de este CSV).
    t0 = df["timestamp"].iloc[0]
    df["t_rel"] = (df["timestamp"] - t0).dt.total_seconds()
    return df


def make_label(df: pd.DataFrame, fallback: str) -> str:
    stacks = df["stack"].dropna().unique()
    if len(stacks) == 1:
        return str(stacks[0])
    return fallback


def plot_dataframes(dfs: list[tuple[pd.DataFrame, str]], out_path: Path,
                    title: str | None, smooth: int) -> None:
    fig, axes = plt.subplots(3, 2, figsize=(13, 9), sharex=True)
    axes = axes.flatten()

    for ax, (col, label) in zip(axes, PANELS):
        for df, series_label in dfs:
            y = df[col]
            if smooth > 1:
                y = y.rolling(smooth, min_periods=1).mean()
            ax.plot(df["t_rel"], y, label=series_label, linewidth=1.5)
        ax.set_title(label)
        ax.set_ylabel("B/s" if "bps" in col else "")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper right", fontsize=9)

    axes[-2].set_xlabel("tiempo relativo (s)")
    axes[-1].set_xlabel("tiempo relativo (s)")

    if title:
        fig.suptitle(title, fontsize=14)
    else:
        if len(dfs) == 1:
            fig.suptitle(f"I/O en réplica — {dfs[0][1]}", fontsize=14)
        else:
            labels = " vs ".join(s for _, s in dfs)
            fig.suptitle(f"I/O en réplica — {labels}", fontsize=14)

    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    print(f"Wrote {out_path}", file=sys.stderr)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("csv", nargs="+", help="Uno o dos CSVs producidos por monitor-mysqlX.sh")
    p.add_argument("-o", "--out", default="monitoring-report.png", help="Ruta del PNG de salida")
    p.add_argument("--title", default=None, help="Título principal del reporte")
    p.add_argument("--smooth", type=int, default=1, help="Tamaño de rolling mean (default 1 = sin suavizado)")
    args = p.parse_args(argv)
    if len(args.csv) > 2:
        p.error("máximo 2 CSVs")
    if args.smooth < 1:
        p.error("--smooth debe ser >= 1")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    dfs: list[tuple[pd.DataFrame, str]] = []
    for i, path_str in enumerate(args.csv):
        path = Path(path_str)
        try:
            df = load_csv(path)
        except (FileNotFoundError, ValueError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 2
        label = make_label(df, fallback=f"csv{i+1}")
        dfs.append((df, label))

    plot_dataframes(dfs, Path(args.out), args.title, args.smooth)
    return 0


if __name__ == "__main__":
    sys.exit(main())
