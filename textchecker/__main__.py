"""
Main entrypoint
"""

import requests

SPELLCHECK_URL = "https://orthographe.reverso.net/api/v1/Spelling"
FAKE_USER_AGENT = "Mozilla/5.0 (Windows NT 6.2; rv:20.0) Gecko/20121202 Firefox/20.0"


def spell_check(text, language="fra"):
    """
    Check the spelling of the ``text``.

    :param text: Text to check, should be smaller or do exactly 450 chars
    :param language: Text's language
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
    return response


if __name__ == "__main__":
    res = spell_check("Bonjor")
    print(res, res.text)
