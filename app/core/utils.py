"""Project-wide utils."""

import re
import logging


CONSOLE = logging.getLogger("commands")


def split_text(text, **kwargs):
    """
    Splits text by either spaces and \n, or by kwargs['pattern'].
    """
    pattern = kwargs.get("pattern", None)
    if pattern is None:
        pattern = r'\s+|\n+'
    return [x.strip() for x in re.split(pattern, text) if x != '']


def extract_hashtags(text):
    return re.findall(r"#(\w+)", text)
