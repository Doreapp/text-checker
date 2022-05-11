"""
Main entrypoint
"""

import requests

from .colors import on_green, on_red

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
        f"{SPELLCHECK_URL}?text={text}&language={language}&getCorrectionDetails=true",
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


def print_spell_check_results(text: str, result: dict):
    """
    Print properly results
    """
    index = 0
    result_text = ""
    for correction in result["corrections"]:
        result_text += text[index : correction["startIndex"]]
        suggestions_text = build_suggestion_text(correction["suggestions"])
        result_text += on_red(correction["mistakeText"]) + on_green(suggestions_text)
        index = correction["endIndex"] + 1
    result_text += text[index:]
    print(result_text)


def main():
    """Main entrypoint"""
    text = "Bonjor, je m'appelle Antoine et j'est 14 ans"
    res = spell_check(text)
    print_spell_check_results(text, res)


if __name__ == "__main__":
    main()
