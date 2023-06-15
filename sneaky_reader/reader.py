import os
import pickle
import sys
from typing import Type
from rich.console import RenderableType
import re
from rich.panel import Panel
from rich.syntax import Syntax
from rich.traceback import Traceback
from textual import events
from textual.app import App, CSSPathType, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.driver import Driver
from textual.reactive import var
from textual.widgets import DirectoryTree, Footer, Header, Static, ListItem, Label, TextLog, LoadingIndicator, OptionList

FAKE_CODE = '''\
def loop_first_last(values: Iterable[T]) -> Iterable[tuple[bool, bool, T]]:
    """Iterate and generate a tuple with a flag for first and last value."""
    iter_values = iter(values)
    try:
        previous_value = next(iter_values)
    except StopIteration:
        return
    first = True
    for value in iter_values:
        yield first, False, previous_value
        first = False
        previous_value = value
    yield first, True, previous_value

class Reader:
    def __init__(self, txt, split_term):
        self._txt = txt
        with open(txt) as f:
            self.content = list(f.readlines())
        self.split_term = re.compile(split_term)
        self.history = 0
        self.find_chapters()
    def find_chapters(self):
        lines = []
        names = []
        for i, l in enumerate(self.content):
            if re.match(self.split_term, l):
                lines.append(i)
                names.append(re.match(self.split_term, l).group(1))
        self.ch_lines = lines
        self.ch_names = names
'''


class Reader:
    def __init__(self, txt, split_term):
        self._txt = txt
        with open(txt) as f:
            self.content = list(f.readlines())
        self.split_term = re.compile(split_term)
        self.history = 0
        self.find_chapters()

    def find_chapters(self):
        lines = []
        names = []
        for i, l in enumerate(self.content):
            if re.match(self.split_term, l.strip()):
                lines.append(i)
                names.append(re.match(self.split_term, l.strip()).group(1))
        self.ch_lines = lines
        self.ch_names = names
        self.index = {n: i for i, n in enumerate(self.ch_names)}

    def get_chapter(self, name):
        index = self.index[name]
        between = (self.ch_lines[index], self.ch_lines[index+1])
        self.history = index
        return "".join(self.content[between[0]:between[1]])

    def get_index(self, index):
        name = self.ch_names[index]
        content = self.get_chapter(name)
        return name, content


class TxtBrowser(App):
    """Textual code browser app."""

    CSS_PATH = "./code_browser.css"
    BINDINGS = [
        ("f", "toggle_files", "Toggle"),
        ("q", "quit", "Quit"),
        ("m", "forward_chapter", "Forward"),
        ("n", "backward_chapter", "Backward"),
        ("s", "switch", "Switch"),
    ]

    show_tree = var(True)
    current_index = var(0)
    boss_mode = var(True)
    
    def __init__(self, *args, **kwargs):
        reader = kwargs.pop("reader", None)
        if reader is None:
            raise ValueError("Must input your reader")
        self.reader = reader
        self.save_path = kwargs.pop("save_path", "./default.pkl")
        super().__init__(*args, **kwargs)

    def watch_show_tree(self, show_tree: bool) -> None:
        """Called when show_tree is modified."""
        self.set_class(show_tree, "-show-tree")
        self.query_one(Footer).visible = show_tree

    def watch_boss_mode(self, boss_mode: bool) -> None:
        """Called when show_tree is modified."""
        self.show_tree = boss_mode
        self.query_one("#code-view", VerticalScroll).visible = boss_mode

    def watch_current_index(self, current_index):
        # self.query_one(ListView).index = current_index
        self.query_one(OptionList).highlighted = current_index

    def compose(self) -> ComposeResult:
        """Compose our UI."""
        with Container():
            yield OptionList(*self.reader.ch_names[:100], id="tree-view")
            yield Static(Syntax(FAKE_CODE, "python"), expand=True, id="fake-code")
            with VerticalScroll(id="code-view"):
                yield Static(id="code", expand=True)
                # yield TextLog(highlight=True, markup=True, id="code")
        yield Footer()

    def on_mount(self, event: events.Mount) -> None:
        self.current_index = self.reader.history
        self.query_one(OptionList).scroll_to_highlight()
        self.query_one(OptionList).focus()
        # self.query_one(ListView).focus()
        name, content = self.reader.get_index(self.reader.history)
        self.update_code_panel(name, content)

    def update_code_panel(self, title, content):
        code_view = self.query_one("#code", Static)
        try:
            syntax = Panel(
                content,
                padding=(0, 0),
                style="color(8)"
            )
        except Exception:
            code_view.update(Traceback(theme="github-dark", width=None))
            self.sub_title = "ERROR"
        else:
            code_view.update(syntax)
            self.query_one("#code-view").scroll_home(animate=False)
            self.sub_title = title
            self.current_index = self.reader.history

    def on_option_list_option_selected(
        self, event: OptionList.OptionSelected
    ) -> None:
        """Called when the user click a file in the directory tree."""
        event.stop()
        name = event.option.prompt
        self.update_code_panel(name, self.reader.get_chapter(name))

    def action_forward_chapter(self) -> None:
        if self.reader.history == len(self.reader.ch_names):
            return
        name = self.reader.ch_names[self.reader.history + 1]
        content = self.reader.get_chapter(name)
        self.update_code_panel(name, content)

    def action_backward_chapter(self):
        if self.reader.history == 0:
            return
        name = self.reader.ch_names[self.reader.history - 1]
        content = self.reader.get_chapter(name)
        self.update_code_panel(name, content)

    def action_toggle_files(self) -> None:
        """Called in response to key binding."""
        self.show_tree = not self.show_tree
        if self.show_tree:
            self.query_one(OptionList).focus()
            self.query_one(OptionList).scroll_to_highlight()

    def action_switch(self):
        self.boss_mode = not self.boss_mode

    def exit(self, *args, **kwargs) -> None:
        pickle.dump(self.reader, open(self.save_path, 'wb'))
        return super().exit(*args, **kwargs)


if __name__ == "__main__":

    TxtBrowser().run()
