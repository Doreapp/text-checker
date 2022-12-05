"""
Spell checkers implementations
"""
import re
import urllib
import html
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

import requests

from textchecker.utils import iterate_with_bar, on_green, on_red

FAKE_USER_AGENT = "Mozilla/5.0 (Windows NT 6.2; rv:20.0) Gecko/20121202 Firefox/20.0"


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


def split_sentence(text: str, max_length) -> list:
    """
    Split a single sentence in several subparts, using " " as separator.
    :param text: Text to split
    :param max_length: Max length of a subpart
    :return: List of the extracted subparts
    """
    parts = text.split(" ")
    return list(merge_text_parts(parts, max_length))


def split_text(text: str, max_length) -> list:
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


def build_suggestion_text(suggestions: List[str]) -> str:
    """
    Build and return a text concatenating ``suggestions``
    """
    return "[" + "|".join(suggestions) + "]"


@dataclass
class SpellCorrection:
    """Spell correction"""

    text: str
    suggestions: List[str]
    start_index: int

    def end_index(self):
        """Return text's end index"""
        return self.start_index + len(self.text)


class SpellCheckResult:
    """Result of a spell check"""

    text: str
    corrections: List[SpellCorrection]

    def __init__(self):
        self.text = ""
        self.corrections = []

    def append_corrections(self, text, corrections: List[SpellCorrection]):
        """Append new corrections"""
        current_length = len(self.text)
        for correction in corrections:
            correction.start_index += current_length
        self.text += text + " "
        self.corrections.extend(corrections)

    def to_string(self) -> str:
        """
        Format results to a single string
        """
        index = 0
        result_text = ""
        for correction in self.corrections:
            result_text += self.text[index : correction.start_index]
            suggestions_text = build_suggestion_text(correction.suggestions)
            result_text += on_red(correction.text) + on_green(suggestions_text)
            index = correction.end_index()
        result_text += self.text[index:]
        return result_text


class SpellChecker(ABC):
    """Abstract spell checker"""

    def __init__(self, url: str, languages: list, max_text_length: int):
        """
        :param url: Url of the checker's API
        :param languages: list of the supported languages
        :param max_text_length: Max text length supported for a single call
        """
        self.url = url
        self.languages = languages
        self.max_text_length = max_text_length

    def split_text(self, text: str) -> list:
        """Split ``text`` accordingly to checker limits"""
        return split_text(text, self.max_text_length)

    @abstractmethod
    def check(self, text: str):
        """Check spelling of ``text``"""


class Reverso(SpellChecker):
    """SpellChecker using reverso technology"""

    def __init__(self):
        super().__init__("https://orthographe.reverso.net/api/v1/Spelling", ("fra", "eng"), 450)

    def _unit_check(self, text: str, language: str) -> dict:
        """Check the spelling of ``text`` using the API"""
        response = requests.get(
            f"{self.url}?text={urllib.parse.quote(text)}&language={language}"
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

    def check(self, text: str, language: str = "fra") -> SpellCheckResult:
        """
        Check the spelling of ``text`` using reverso checker's technology
        """
        if language not in self.languages:
            raise Exception(f"Language '{language}' not supported")
        subparts = self.split_text(text)
        result = SpellCheckResult()
        print("Loading corrections...")
        for subpart in iterate_with_bar(subparts):
            raw_corrections = self._unit_check(subpart, language)
            self._parse_result(result, subpart, raw_corrections["corrections"])
        return result

    @staticmethod
    def _parse_result(current_result: SpellCheckResult, input_text: str, result: dict):
        """
        Parse raw corrections an update ``current_result`` accoringly.
        :param current_result: Current SpellCheckResult, to update
        :param input: Text input, corrected
        :param result: Result from API call
        """
        parsed_corrections = [
            SpellCorrection(
                correction["mistakeText"],
                list(map(lambda correction: correction["text"], correction["suggestions"])),
                correction["startIndex"],
            )
            for correction in result
        ]
        current_result.append_corrections(input_text, parsed_corrections)

class Scribens(SpellChecker):
    """SpellChecker using scrbiens technology"""
    def __init__(self):
        super().__init__("https://www.scribens.fr/Scribens/TextSolution_Servlet", ("fr",), 200000)

    def _unit_check(self, text: str, language: str) -> dict:
        """Check the spelling of ``text`` using the API"""
        response = requests.post(
            self.url,
            headers={
                "Accept": "*/*",
                "Connection": "keep-alive",
                "User-Agent": FAKE_USER_AGENT,
            },
            data={
                "FunctionName": "GetTextSolution",
                "texteHTML": "<p>" + text.replace("\n", "</p><p>") + "</p>",
                "langId": "fr"
            }
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            raise Exception(f"Unable to check spelling of '{text}'") from exc
        return response.json()
    
    def check(self, text: str, language: str = "fr") -> SpellCheckResult:
        """
        Check the spelling of ``text`` using scrbiens checker's technology
        """
        if language not in self.languages:
            raise Exception(f"Language '{language}' not supported")
        subparts = self.split_text(text)
        result = SpellCheckResult()
        print("Loading corrections...")
        for subpart in subparts:
            raw_corrections = self._unit_check(subpart, language)
            self._parse_result(result, subpart, raw_corrections)
        return result
    
    @staticmethod
    def _parse_result(current_result: SpellCheckResult, input_text: str, result: dict):
        """
        Parse raw corrections an update ``current_result`` accoringly.
        :param current_result: Current SpellCheckResult, to update
        :param input: Text input, corrected
        :param result: Result from API call
        """
        print(result)
