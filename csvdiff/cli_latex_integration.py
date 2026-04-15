"""Integration glue: register the 'latex' format with the main CLI."""
from __future__ import annotations

from argparse import ArgumentParser

from csvdiff.core import DiffResult
from csvdiff.cli_latex import handle_latex_output


FORMAT_NAME = "latex"


def add_latex_arguments(parser: ArgumentParser) -> None:
    """Add LaTeX-specific CLI flags to *parser*."""
    group = parser.add_argument_group("LaTeX output options")
    group.add_argument(
        "--no-preamble",
        action="store_true",
        default=False,
        help=(
            "Omit \\usepackage{} declarations. "
            "Useful when embedding the output in an existing .tex file."
        ),
    )


def dispatch_latex(
    diff: DiffResult,
    output_path: str | None,
    no_preamble: bool = False,
) -> None:
    """Entry point called by the main CLI dispatcher for format='latex'.

    Parameters
    ----------
    diff:
        Computed diff result.
    output_path:
        Destination file path, or ``None`` for stdout.
    no_preamble:
        When ``True`` skip ``\\usepackage`` lines.
    """
    handle_latex_output(diff, output_path, preamble=not no_preamble)


# Mapping consumed by cli.py's format dispatcher
FORMAT_HANDLER = {
    FORMAT_NAME: dispatch_latex,
}
