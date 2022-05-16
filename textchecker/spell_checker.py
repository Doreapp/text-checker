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
MAX_TEXT_LENGTH = 450


class SpellChecker:
    """Spell checker of a text"""

    def __init__(self, text: str):
        """
        :param text: Text to check
        """
        self.text = text
        self.corrections = []
        self.full_text = ""

    def check(self):
        """
        Check the text
        """
        subparts = split_text(self.text)
        print("Loading corrections...")
        for index, subpart in enumerate(subparts, start=1):
            print_progress_bar(index, len(subparts))
            result = spell_check(subpart)
            if not result:
                print()  # Finish progress bar line
                print(on_red("/!\\ Spell check refused by server."))
                break
            self.append_results(subpart, result["corrections"])

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

    def print_results(self):
        """
        Properly print corrections.
        Should be called after ``check()`` function.
        """
        index = 0
        result_text = ""
        for correction in self.corrections:
            result_text += self.full_text[index : correction["startIndex"]]
            suggestions_text = build_suggestion_text(correction["suggestions"])
            result_text += on_red(correction["mistakeText"]) + on_green(suggestions_text)
            index = correction["endIndex"] + 1
        result_text += self.full_text[index:]
        print(result_text)


def spell_check(text: str, language: str = "fra") -> dict:
    """
    Check the spelling of the ``text``.

    :param text: Text to check, should be smaller or do exactly ``MAX_TEXT_LENGTH`` chars
    :param language: Text's language
    :return: Response from reverso. None if the server refused to respond.
    """
    if language not in SUPPORTED_LANGUAGES:
        raise Exception(f"Language '{language}' not supported")
    if len(text) > MAX_TEXT_LENGTH:
        raise Exception(
            f"Text is too long. length={len(text)}, max={MAX_TEXT_LENGTH}, text='{text}'."
        )
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
        if response.status_code == 429:
            return None
        raise Exception(f"Unable to check spelling of '{text}'") from exc

    return response.json()


def build_suggestion_text(suggestions: list) -> str:
    """
    Build and return a text concatenating ``suggestions``
    """
    texts = map(lambda suggestion: suggestion["text"], suggestions)
    return "[" + "|".join(texts) + "]"


def merge_text_parts(parts: list, max_length, join=" ") -> list:
    """
    Merge a list of text parts in longer parts
    :param parts: List of strings to merge
    :param max_length: Max length to reach but not exceed
    :param join: Text to add between parts
    :return: List of the merged subparts
    """
    current_part = ""
    join_length = len(join)
    for part in parts:
        if len(part) > max_length:
            raise Exception(
                "Unable to split the text in small-enough parts. Problematic section: " + part
            )
        if len(current_part) + len(part) + join_length > max_length:
            yield current_part
            current_part = part
        else:
            current_part += join + part
    yield current_part


def split_sentence(text: str, max_length=MAX_TEXT_LENGTH) -> list:
    """
    Split a single sentence in several subparts, using " " as separator.
    :param text: Text to split
    :param max_length: Max length of a subpart
    :return: List of the extracted subparts
    """
    parts = text.split(" ")
    return list(merge_text_parts(parts, max_length))


def split_text(text: str, max_length=MAX_TEXT_LENGTH) -> list:
    """
    Split a string in several subparts.
    Try to maximize the size of subparts, while remaining bellow ``max_length``.
    :param text: Text to split
    :param max_length: Max length of a subpart
    :return: List of extracted subparts
    """
    parts = re.split(r"(.+[\n.?!:])", text)
    cleaned_parts = []
    for part in parts:
        part = part.strip()
        if len(part) > max_length:
            cleaned_parts.extend(split_sentence(part, max_length))
        else:
            cleaned_parts.append(part)
    return list(merge_text_parts(cleaned_parts, max_length))
