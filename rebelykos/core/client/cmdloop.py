import asyncio
import functools
import logging
import shlex

from docopt import docopt, DocoptExit
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.application import run_in_terminal
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.formatted_text import HTML
from terminaltables import SingleTable

from rebelykos.core.client.contexts.teamservers import TeamServers
from rebelykos.core.client.utils import cmd, register_cli_cmds

class RLCompleter(Completer):
    def __init__(self, cli_menu):
        self.cli_menu = cli_menu

    # currently just dummy
    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor()
        try:
            cmd_line = [s.lower() for s in shlex.split(document.current_line)]
        except ValueError:
            pass
        else:
            for cmd in cmd_line:
                yield Completion(cmd, -len(word_before_cursor))

@register_cli_cmds
class RLShell:
    name = "main"
    description = "Main menu"
    _remote = False

    def __init__(self, args):
        self.args = args
        self.current_context = self
        self.teamservers = TeamServers(args['<URL>'])
        self.completer = RLCompleter(self)
        self.prompt_session = PromptSession(
            HTML("RL >> "),
            completer=self.completer,
            complete_in_thread=True,
            complete_while_typing=True,
            auto_suggest=AutoSuggestFromHistory(),
            search_ignore_case=True
        )

    def get_context(self, ctx_name=None):
        try:
            cli_menus = [*self.teamservers.selected.contexts, self.teamservers]
        except AttributeError:
            cli_menus = [self.teamservers]

        if ctx_name:
            return [c for c in cli_menus if c.name == ctx_name][0]
        return cli_menus

    async def update_prompt(self, ctx):
        self.prompt_session.message = HTML(
            ("[<ansiyellow>"
             f"{len(self.teamservers.connections)}"
             f"</ansiyellow>] RL (<ansired>{ctx.name}</ansired>)"
             f"{' >> ' if not ctx.prompt else ctx.prompt + ' >> ' }")
        )

    async def switched_context(self, text):
        for ctx in self.get_context():
            if text.lower() == ctx.name:
                if ctx._remote is True:
                    try:
                        res = await self.teamservers.send(ctx=ctx.name,
                                                          cmd="get_selected")
                        if res.result:
                            ctx.selected = res.result
                    except AttributeError:
                        break

                await self.update_prompt(ctx)
                self.current_context = ctx
                return True
        return False

    async def parse_cmd_line(self, text):
        if not await self.switched_context(text):
            try:
                cmd = shlex.split(text)
                logging.debug(f"command: {cmd[0]} args: {cmd[1:]} "
                              f"ctx: {self.current_context.name}")
                args = docopt(
                    getattr(
                        self.current_context if hasattr(self.current_context,
                                                        cmd[0]) else self,
                        cmd[0]
                    ).__doc__,
                    argv=cmd[1:]
                )
            except ValueError as e:
                print(f"Error parsing command: {e}")
            except AttributeError as e:
                print(f"Unknown command '{cmd[0]}'")
            except (DocoptExit, SystemExit):
                pass
            else:
                if cmd[0] in self._cmd_registry or \
                        self.current_context._remote is False:
                    run_in_terminal(
                        functools.partial(
                            getattr(self if cmd[0] in self._cmd_registry
                                    else self.current_context,
                                    cmd[0]),
                            args=args
                        )
                    )
                elif self.current_context._remote is True:
                    res = await self.teamservers.send(
                        ctx=self.current_context.name,
                        cmd=cmd[0],
                        args=args
                    )
                    logging.debug(f"response: {res}")
                    if res.status == "success" and res.result:
                        if hasattr(self.current_context, cmd[0]):
                            run_in_terminal(
                                functools.partial(
                                    getattr(self.current_context, cmd[0]),
                                    args=args,
                                    response=res
                                )
                            )
                    elif res.status == "error":
                        print(res.result)
                if self.current_context.name != "main":
                    await self.update_prompt(self.current_context)

    async def cmdloop(self):
        while True:
            with patch_stdout():
                text = await self.prompt_session.prompt_async()
                if len(text):
                    if text.lower() == "exit":
                        break

                    await self.parse_cmd_line(text)

    @cmd
    def help(self):
        """
        Shows available commands

        Usage: help
        """
        table_data = [["Command", "Description"]]

        try:
            for cmd in self.current_context._cmd_registry:
                table_data.append([
                    cmd,
                    getattr(
                        self.current_context,
                        cmd
                    ).__doc__.split("\n", 2)[1].strip()
                ])
            for menu in self.get_context():
                if menu.name != self.current_context.name:
                    table_data.append([menu.name, menu.description])
        except AttributeError:
            for menu in self.get_context():
                table_data.append([menu.name, menu.description])

        table = SingleTable(table_data)
        print(table.table)
