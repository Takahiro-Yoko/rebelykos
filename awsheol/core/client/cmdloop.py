import asyncio
import shlex

from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.application import run_in_terminal
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.formatted_text import HTML

class AWShCompleter(Completer):
    def __init__(self, cli_menu):
        self.cli_menu = cli_menu

    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor()
        try:
            cmd_line = [s.lower() for s in shlex.split(document.current_line)]
        except ValueError:
            pass
        else:
            if len(cmd_line):
                pass

class AWShell:
    def __init__(self, args):
        self.args = args
        self.current_context = self
        self.completer = AWShCompleter(self)
        self.prompt_session = PromptSession(
            HTML("AWSh >> "),
            completer=self.completer,
            complete_in_thread=True,
            complete_while_typing=True,
            auto_suggest=AutoSuggestFromHistory(),
            search_ignore_case=True
        )

    async def parse_cmd_line(self, text):
        # asyncio.sleep(0.5)
        print(text)

    async def cmdloop(self):
        while True:
            with patch_stdout():
                text = await self.prompt_session.prompt_async()
                if len(text):
                    if text.lower() == "exit":
                        break

                    await self.parse_cmd_line(text)
