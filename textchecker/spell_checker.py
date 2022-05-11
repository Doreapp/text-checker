"""
Spell checker
"""

import urllib

import requests

from .utils import on_green, on_red, print_progress_bar

SPELLCHECK_URL = "https://orthographe.reverso.net/api/v1/Spelling"
FAKE_USER_AGENT = "Mozilla/5.0 (Windows NT 6.2; rv:20.0) Gecko/20121202 Firefox/20.0"
SUPPORTED_LANGUAGES = ("fra", "eng")


class SpellChecker:
    """Spell checker of a text"""

    def __init__(self, text: str):
        self.text = text
        self.result_builder = self.ResultBuilder()

    def check(self):
        """
        Check the text
        """
        sentences = split_sentences(self.text)
        print("Loading corrections...")
        for index, sentence in enumerate(sentences, start=1):
            print_progress_bar(index, len(sentences))
            result = spell_check(sentence)
            self.result_builder.append_results(sentence, result["corrections"])

    def print_results(self):
        """
        Print properly corrections
        :param text: Text checked
        :param corrections: corrections suggested
        """
        index = 0
        result_text = ""
        for correction in self.result_builder.corrections:
            result_text += self.text[index : correction["startIndex"]]
            suggestions_text = build_suggestion_text(correction["suggestions"])
            result_text += on_red(correction["mistakeText"]) + on_green(suggestions_text)
            index = correction["endIndex"] + 1
        result_text += self.text[index:]
        print(result_text)

    class ResultBuilder:  # pylint: disable=too-few-public-methods
        """Build of full reverso result"""

        def __init__(self):
            self.corrections = []
            self.end_index = 0

        def append_results(self, text: str, corrections: list):
            """
            Append corrections to global results
            :param text: Text checked
            :corrections: List of corrections to apply
            """
            for correction in corrections:
                correction["startIndex"] += self.end_index
                correction["endIndex"] += self.end_index
                self.corrections.append(correction)
            self.end_index += len(text)


def spell_check(text: str, language: str = "fra") -> dict:
    """
    Check the spelling of the ``text``.

    :param text: Text to check, should be smaller or do exactly 450 chars
    :param language: Text's language
    :return: Response from reverso
    """
    if language not in SUPPORTED_LANGUAGES:
        raise Exception(f"Language '{language}' not supported")
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


def split_sentences(text: str) -> list:
    """
    Split a string in several sentences
    """
    sentences = text.split(".")
    return list(map(lambda sentence: sentence + ".", sentences))
