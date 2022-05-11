"""
Main entrypoint
"""

import argparse
import sys
import urllib

import requests

from .utils import on_green, on_red, print_progress_bar

SPELLCHECK_URL = "https://orthographe.reverso.net/api/v1/Spelling"
FAKE_USER_AGENT = "Mozilla/5.0 (Windows NT 6.2; rv:20.0) Gecko/20121202 Firefox/20.0"


def spell_check(text: str, language: str = "fra") -> dict:
    """
    Check the spelling of the ``text``.

    :param text: Text to check, should be smaller or do exactly 450 chars
    :param language: Text's language
    :return: Response from reverso
    """
    response = requests.get(
        f"{SPELLCHECK_URL}?text={urllib.parse.quote(text)}&language={language}"
        "&getCorrectionDetails=true",
        headers={
            "Accept": "*/*",
            "Connection": "keep-alive",
            "User-Agent": FAKE_USER_AGENT,
        },
    )
    response.raise_for_status()
    return response.json()


def build_suggestion_text(suggestions: list) -> str:
    """
    Build and return a text concatenating suggestions
    """
    suggestions_text = "["
    for pos, suggestion in enumerate(suggestions):
        if pos > 0:
            suggestions_text += "|"
        suggestions_text += suggestion["text"]
    suggestions_text += "]"
    return suggestions_text


def print_spell_check_results(text: str, corrections: dict):
    """
    Print properly corrections
    """
    index = 0
    result_text = ""
    for correction in corrections:
        result_text += text[index : correction["startIndex"]]
        suggestions_text = build_suggestion_text(correction["suggestions"])
        result_text += on_red(correction["mistakeText"]) + on_green(suggestions_text)
        index = correction["endIndex"] + 1
    result_text += text[index:]
    print(result_text)


def split_sentences(text: str) -> list:
    """
    Split a string in several sentences
    """
    sentences = text.split(".")
    return list(map(lambda sentence: sentence + ".", sentences))


class ResultBuilder:  # pylint: disable=too-few-public-methods
    """Build of full reverso result"""

    def __init__(self):
        self.corrections = []
        self.end_index = 0

    def append_results(self, text: str, corrections: list):
        """
        Append corrections to full results
        :param text: Text corrected
        :corrections: List of corrections to apply
        """
        for correction in corrections:
            correction["startIndex"] += self.end_index
            correction["endIndex"] += self.end_index
            self.corrections.append(correction)
        self.end_index += len(text)


def get_cli_parser() -> argparse.ArgumentParser:
    """Build and return CLI parser"""
    parser = argparse.ArgumentParser(
        "textchecker", description="Program to checker a text", epilog="Built by Antoine MANDIN"
    )
    parser.add_argument("path", help="Path to the file containing the text to check")
    return parser


def check_text(text: str):
    """
    Check the text
    """
    sentences = split_sentences(text)
    builder = ResultBuilder()
    print("Loading corrections...")
    for index, sentence in enumerate(sentences, start=1):
        print_progress_bar(index, len(sentences))
        result = spell_check(sentence)
        builder.append_results(sentence, result["corrections"])
    print_spell_check_results(text, builder.corrections)


def main(cli: list):
    """
    Main entrypoint
    :param cli: Command line arguments
    """
    arguments = get_cli_parser().parse_args(cli)
    with open(arguments.path, "r", encoding="utf8") as stream:
        text = stream.read()
    check_text(text)


if __name__ == "__main__":
    main(sys.argv[1:])
