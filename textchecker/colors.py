"""
Utilities to get colored text
"""

HEADER = "\033[95m"
OKBLUE = "\033[94m"
OKCYAN = "\033[96m"
OKGREEN = "\033[92m"
WARNING = "\033[93m"
FAIL = "\033[91m"
ENDC = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"


def on_green(text):
    """Return the text on green background"""
    return f"{OKGREEN}{text}{ENDC}"


def on_red(text):
    """Return the text on red background"""
    return f"{FAIL}{text}{ENDC}"
