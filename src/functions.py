import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

import time
import random
import uuid
import os
import glob
import dateparser
import logging
import frontmatter
from jinja2 import Template
from pathlib import Path
from ulauncher.utils.fuzzy_search import get_score
from typing import List


logger = logging.getLogger(__name__)


class Snippet:
    """
    >>> s = Snippet('date.j2', 'test-snippets/date.j2')
    >>> s.render()
    '[[2020-12-09]] <== <button class="date_button_today">Today</button> ==> [[2020-12-11]]'

    >>> s = Snippet('frontmatter.j2', 'test-snippets/frontmatter.j2')
    >>> s.render()
    'Here is the content\\n\\n2020-12-10\\n\\nHi'

    >>> s = Snippet('frontmatter.j2', 'test-snippets/frontmatter.j2')
    >>> s.next_variable()
    {'label': 'Name of the component'}

    >>> s.variables["name"]["value"] = "Set"
    >>> s.next_variable()
    {'label': 'With default', 'default': 'Hi'}

    >>> s.get_variable("name")
    'Set'

    >>> s.get_variable("other_var")
    'Hi'
    """

    def __init__(self, name: str, path: str):
        snippet = frontmatter.load(path)

        self.variables = snippet.get("vars", {})
        self.name = snippet.get("name", name[:-3])
        self.icon = snippet.get("icon", "images/icon.png")
        self.path = path
        self.description = snippet.get("description", snippet.content[:40])

    def render(self, args=[]) -> str:
        snippet = frontmatter.load(self.path)
        template = Template(snippet.content)
        return template.render(
            date=date,
            clipboard=clipboard,
            random_int=random_int,
            random_item=random_item,
            random_uuid=random_uuid,
            vars=self.get_variable
        )

    def next_variable(self):
        for id, variable in self.variables.items():
            if not variable.get("value"):
                return variable
        return None

    def get_variable(self, name):
        var = self.variables.get(name)
        default = var.get("default", "")
        value = var.get("value", default)
        return value

    def __repr__(self):
        return self.name


def fuzzyfinder(search: str, items: List[str]) -> List[str]:
    """
    >>> fuzzyfinder("hallo", ["hi", "hu", "hallo", "false"])
    ['hallo', 'false', 'hi', 'hu']
    """
    scores = []
    for i in items:
        score = get_score(search, i)
        scores.append((score, i))

    scores = sorted(scores, key=lambda score: score[0], reverse=True)

    return list(map(lambda score: score[1], scores))


def random_uuid() -> str:
    return uuid.uuid4().hex


def random_int(min: int, max: int) -> int:
    return random.randint(min, max)


def random_item(list: List[str]) -> str:
    return random.choice(list)


def date(expression: str, format: str = "%Y-%m-%d") -> str:
    """
    >>> date("last year", "%Y")
    '2019'

    >>> date("", "%B")
    ''
    """
    dt = dateparser.parse(expression)
    if dt is not None:
        formatted_dt = dt.strftime(format)
        return formatted_dt
    return ""


def clipboard() -> str:
    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    text = clipboard.wait_for_text()

    if text is not None:
        return text

    return ""


def get_snippets(path: str, search: str) -> List[Snippet]:
    """
    >>> get_snippets("test-snippets", "react")
    [react/component, date, Frontmatter Snippet, placeholder, go]
    """
    search_pattern = os.path.join(path, "**", "*.j2")
    logger.info(search_pattern)
    files = glob.glob(search_pattern, recursive=True)
    suggestions = fuzzyfinder(search, files)

    return [
        Snippet(name=str(Path(f).relative_to(path)), path=f) for f in suggestions
    ]


if __name__ == "__main__":
    import doctest
    from freezegun import freeze_time
    freezer = freeze_time("2020-12-10 12:00:01")
    freezer.start()
    doctest.testmod()
    freezer.stop()
