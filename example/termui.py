#  Copyright 2025 Shoji Kumagai
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import annotations

import contextlib
import enum
import os
import warnings
from typing import TYPE_CHECKING

import rich
from rich.box import ROUNDED
from rich.console import Console
from rich.progress import Progress, ProgressColumn
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table
from rich.theme import Theme


if TYPE_CHECKING:
    from typing import Any, Sequence

    from example._types import RichProtocol, Spinner, SpinnerT


DEFAULT_THEME = {
    "primary": "cyan",
    "success": "green",
    "warning": "yellow",
    "error": "red",
    "info": "blue",
    "req": "bold green",
}

_error_console = Console(stderr=True, theme=Theme(DEFAULT_THEME))


def is_interactive(console: Console | None = None) -> bool:
    """Check if the terminal is run under interactive mode"""
    if console is None:
        console = rich.get_console()
    return "EXAMPLE_CLI_NON_INTERACTIVE" not in os.environment and console.is_interactive


def is_legacy_windows(console: Console | None = None) -> bool:
    """Legacy Windows renderer may have problem rendering emojis"""
    if console is None:
        console = rich.get_console()
    return console.legacy_windows


def style(text: str, *args: str, style: str | None = None, **kwargs: Any) -> str:
    """return text with ansi codes using rich console"""
    _console = rich.get_console()
    if _console.legacy_windows or not _console.is_terminal:
        return text
    with _console.capture() as capture:
        _console.print(text, *args, end="", style=style, **kwargs)
    return capture.get()


def confirm(*args: str, **kwargs: Any) -> bool:
    default = kwargs.setdefault("default", False)
    if not is_interactive():
        return default
    return Confirm.ask(*args, **kwargs)


def ask(*args: str, prompt_type: type[str] | type[int] | None = None, **kwargs: Any) -> str:
    """prompt user and return response"""
    if not prompt_type or prompt_type is str:
        return Prompt.ask(*args, **kwargs)
    elif prompt_type is int:
        return str(IntPrompt.ask(*args, **kwargs))
    else:
        raise ValueError(f"unsupported {prompt_type}")


class Verbosity(enum.IntEnum):
    QUIET = -1
    NORMAL = 0
    DETAIL = 1
    DEBUG = 2


class Emoji:
    if is_legacy_windows():
        SUCCESS = "v"
        FAIL = "x"
        LOCK = " "
        POPPER = " "
        ELLIPSIS = "..."
        ARROW_SEPARATOR = ">"
    else:
        SUCCESS = ":heavy_check_mark:"
        FAIL = ":heavy_multiplication_x:"
        LOCK = ":lock:"
        POPPER = ":party_popper:"
        ELLIPSIS = "…"
        ARROW_SEPARATOR = "➤"


if is_legacy_windows():
    SPINNER = "line"
else:
    SPINNER = "dots"


class DummySpinner:
    """A dummy spinner class implementing needed interfaces.
    But only display text onto screen.
    """

    def __init__(self, text: str) -> None:
        self.text = text

    def _show(self) -> None:
        _error_console.print(f"[primary]STATUS:[/] {self.text}")

    def update(self, text: str) -> None:
        self.text = text
        self._show()

    def __enter__(self: SpinnerT) -> SpinnerT:
        self._show()  # type: ignore[attr-defined]
        return self

    def __exit__(self, *args: Any) -> None:
        pass


class SilentSpinner(DummySpinner):
    def _show(self) -> None:
        pass


class UI:
    """Terminal UI object"""

    def __init__(
        self,
        verbosity: Verbosity = Verbosity.NORMAL,
        *,
        exit_stack: contextlib.ExitStack | None = None
    ) -> None:
        self.verbosity = verbosity
        self.exit_stack = exit_stack or contextlib.ExitStack()

    def set_verbosity(self, verbosity: int) -> None:
        self.verbosity = Verbosity(verbosity)
        if verbosity == Verbosity.QUIET:
            self.exit_stack.enter_context(warnings.catch_warnings())
            warnings.simplefilter("ignore", FutureWarning, append=True)

    def set_theme(self, theme: Theme) -> None:
        rich.get_console().push_theme(theme)
        _error_console.push_theme(theme)

    def echo(
        self,
        message: str | RichProtocol = "",
        err: bool = False,
        verbosity: Verbosity = Verbosity.QUIET,
        **kwargs: Any,
    ) -> None:
        """print message using rich console.

        """
        if self.verbosity >= verbosity:
            console = _error_console if err else rich.get_console()
            if not console.is_interactive:
                kwargs.setdefault("crop", False)
                kwargs.setdefault("overflow", "ignore")
            console.print(message, **kwargs)

    def display_columns(self, rows: Sequence[Sequence[str]], header: list[str] | None = None) -> None:
        """Print rows in aligned columns.

        """
        if header:
            table = Table(box=ROUNDED)
            for title in header:
                if title[0] == "^":
                    title, justify = title[1:], "center"
                elif title[0] == ">":
                    title, justify = title[1:], "right"
                else:
                    title, justify = title, "left"
                table.add_column(title, justify=justify)
        else:
            table = Table.grid(padding=(0, 1))
            for _ in rows[0]:
                table.add_column()
        for row in rows:
            table.add_row(*row)

        rich.print(table)

    def open_spinner(self, title: str) -> Spinner:
        """Open a spinner as a context manager."""
        if self.verbosity >= Verbosity.DETAIL or not is_interactive():
            return DummySpinner()
        else:
            return _error_console.status(title, spinner=SPINNER, spinner_style="primary")

    def make_progress(self, *columns: str | ProgressColumn, **kwargs: Any) -> Progress:
        """create a progress instance for indented spinners"""
        return Progress(*columns, disable=self.verbosity >= Verbosity.DETAIL, **kwargs)

    def info(self, message: str, verbosity: Verbosity = Verbosity.NORMAL) -> None:
        """Print a message to stdout."""
        self.echo(f"[info]INFO:[/] [dim]{message}[/]", err=True, verbosity=verbosity)

    def deprecated(self, message: str, verbosity: Verbosity = Verbosity.NORMAL) -> None:
        """Print a message to stdout."""
        self.echo(f"[warning]DEPRECATED:[/] [dim]{message}[/]", err=True, verbosity=verbosity)

    def warn(self, message: str, verbosity: Verbosity = Verbosity.NORMAL) -> None:
        """Print a message to stdout."""
        self.echo(f"[warning]WARNING:[/] {message}", err=True, verbosity=verbosity)

    def error(self, message: str, verbosity: Verbosity = Verbosity.QUIET) -> None:
        """Print a message to stdout."""
        self.echo(f"[error]ERROR:[/] {message}", err=True, verbosity=verbosity)
