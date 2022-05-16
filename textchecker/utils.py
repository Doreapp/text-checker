"""
Utilities
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


def print_progress_bar(progress, max_progress, bar_width=60):
    """
    Print a progress bar on the console.
    Use in a raw

    :param progress: Current progress
    :param max_progress: Max progress to reach
    :param bar_width: Char width of the bar
    """
    percent = 100 * float(progress) / float(max_progress)
    filled_width = int(bar_width * float(progress) / float(max_progress) + 0.5)
    progress_bar = "█" * filled_width
    progress_bar += "▒" * (bar_width - filled_width)
    print(f"\r {progress_bar}  {percent:.0f}%", end="\r")
    if progress == max_progress:
        print()


def iterate_with_bar(iterable, length=None):
    """
    Iterate through the iterable, while displaying a progress bar
    :param iterable:
    :param length: size of iterable. If None, will use len(iterable).
    """
    if length is None:
        length = len(iterable)
    for index, value in enumerate(iterable):
        yield value
        print_progress_bar(index, length)
