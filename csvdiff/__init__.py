"""csvdiff — A command-line tool for diffing large CSV files."""

from csvdiff.core import diff_csvs, DiffResult, load_csv

__all__ = ["diff_csvs", "DiffResult", "load_csv"]
__version__ = "0.1.0"
