"""
Main entrypoint
"""

import argparse
import html
import sys

from .checkers import Reverso, Scribens


def get_cli_parser() -> argparse.ArgumentParser:
    """Build and return CLI parser"""
    parser = argparse.ArgumentParser(
        "textchecker", description="Program to checker a text", epilog="Built by Antoine MANDIN"
    )
    parser.add_argument("path", help="Path to the file containing the text to check")
    return parser


def main(cli: list):
    """
    Main entrypoint
    :param cli: Command line arguments
    """
    arguments = get_cli_parser().parse_args(cli)
    with open(arguments.path, "r", encoding="utf8") as stream:
        text = stream.read()
    spell_checker = Scribens()
    results = spell_checker.check(text)
    print(results.to_string())


if __name__ == "__main__":
    main(sys.argv[1:])
