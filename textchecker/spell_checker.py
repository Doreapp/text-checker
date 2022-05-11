"""
Spell checker
"""

import re
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
        subparts = split_text(self.text)
        print("Loading corrections...")
        for index, subpart in enumerate(subparts, start=1):
            print_progress_bar(index, len(subparts))
            result = spell_check(subpart)
            self.result_builder.append_results(subpart, result["corrections"])

    def print_results(self):
        """
        Print properly corrections
        :param text: Text checked
        :param corrections: corrections suggested
        """
        index = 0
        result_text = ""
        for correction in self.result_builder.corrections:
            result_text += self.result_builder.full_text[index : correction["startIndex"]]
            suggestions_text = build_suggestion_text(correction["suggestions"])
            result_text += on_red(correction["mistakeText"]) + on_green(suggestions_text)
            index = correction["endIndex"] + 1
        result_text += self.result_builder.full_text[index:]
        print(result_text)

    class ResultBuilder:  # pylint: disable=too-few-public-methods
        """Build of full reverso result"""

        def __init__(self):
            self.corrections = []
            self.full_text = ""

        def append_results(self, text: str, corrections: list):
            """
            Append corrections to global results
            :param text: Text checked
            :corrections: List of corrections to apply
            """
            for correction in corrections:
                correction["startIndex"] += len(self.full_text)
                correction["endIndex"] += len(self.full_text)
                self.corrections.append(correction)
            self.full_text += text + " "


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
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        raise Exception(f"Unable to check spelling of '{text}'") from exc

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


def split_sentence(text: str, max_length=450) -> list:
    """
    Split a single sentence in several subparts
    """
    parts = text.split(" ")
    merged_parts = []
    current_part = ""
    for part in parts:
        if len(current_part) + len(part) + 1 > max_length:
            merged_parts.append(current_part)
            current_part = part
        else:
            current_part += " " + part
    merged_parts.append(current_part)
    return merged_parts


def split_text(text: str, max_length=450) -> list:
    """
    Split a string in several sub-parts.
    Try to maximize the size of subparts, while remaining bellow ``max_length``.

    :param text: Text to split
    :param max_length: Max length of a sub-part
    :return: List of extracted subparts
    """
    parts = re.split(r"(.+[\n.?!:])", text)
    cleaned_parts = []
    for part in parts:
        part = part.strip()
        if len(part) == 0:
            continue
        if len(part) > max_length:
            cleaned_parts.extend(split_sentence(part, max_length))
        else:
            cleaned_parts.append(part)
    for part in cleaned_parts:
        if len(part) > max_length:
            raise Exception(
                "Unable to split the text in small-enough parts. Problematic section: " + part
            )
    merged_parts = []
    current_part = ""
    for part in cleaned_parts:
        if len(current_part) + len(part) > max_length:
            merged_parts.append(current_part)
            current_part = part
        else:
            current_part += " " + part
    merged_parts.append(current_part)  # Add last one
    return merged_parts
