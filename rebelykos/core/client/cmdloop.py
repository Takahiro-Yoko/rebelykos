import asyncio
import functools
import logging
import shlex
import shutil

from docopt import docopt, DocoptExit
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.application import run_in_terminal
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.formatted_text import HTML
from terminaltables import SingleTable

from rebelykos.core.utils import print_bad
from rebelykos.core.client.contexts.teamservers import TeamServers
from rebelykos.core.client.utils import cmd, register_cli_cmds


def bottom_toolbar(ts):
    if ts.selected and ts.selected.stats.CONNECTED:
        ts = ts.selected
        terminal_width, _ = shutil.get_terminal_size()
        info_bar1 = (f"{ts.alias} - {ts.url.scheme}://{ts.url.username}"
                     f"@{ts.url.hostname}:{ts.url.port}")
        info_bar2 = (f"[Users: {len(ts.stats.USERS)}]")
        ljustify_amount = terminal_width - len(info_bar2)
        return HTML(f"{info_bar1:<{ljustify_amount}}{info_bar2}")
    return HTML('<b><style bg="ansired">Disconnected</style></b>')

class RLCompleter(Completer):
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
                if self.cli_menu.current_context.name == "teamservers":
                    if cmd_line[0] in \
                            self.cli_menu.current_context._cmd_registry:
                        for conn in self.cli_menu.current_context.connections:
                            if conn.stats.CONNECTED and \
                                    conn.alias.startswith(word_before_cursor):
                                yield Completion(conn.alias,
                                                 -len(word_before_cursor))

                if self.cli_menu.current_context.name == "profiles":
                    if cmd_line[0] == "set":
                        if len(cmd_line) < 3:
                            for name in ("access_key_id",
                                         "secret_access_key",
                                         "region",
                                         "session_token",
                                         "profile"):
                                if name.startswith(word_before_cursor):
                                    yield Completion(name,
                                                     -len(word_before_cursor))
                        return
                    elif cmd_line[0] in ("use", "remove"):
                        if len(cmd_line) < 3:
                            profiles = self.cli_menu.get_context("profiles")
                            for profile in profiles.profiles:
                                if profile.startswith(word_before_cursor):
                                    yield Completion(
                                            profile,
                                            -len(word_before_cursor)
                                    )
                        return

                if self.cli_menu.teamservers.selected:
                    if cmd_line[0] == "use":
                        for loadable in \
                                self.cli_menu.current_context.available:
                            if word_before_cursor in loadable:
                                try:
                                    yield Completion(loadable,
                                                     -len(cmd_line[1]))
                                except IndexError:
                                    yield Completion(loadable,
                                                     -len(word_before_cursor))
                        return
                    elif 2 <= len(cmd_line) <= 3 and cmd_line[0] == "set" \
                            and cmd_line[1] == "profile":
                        profiles = self.cli_menu.get_context("profiles")
                        for profile in profiles.profiles:
                            if profile.startswith(word_before_cursor):
                                yield Completion(
                                        profile,
                                        -len(word_before_cursor)
                                )
                        return

                if hasattr(self.cli_menu.current_context, "selected") and \
                        self.cli_menu.current_context.selected:
                    if cmd_line[0] == "set":
                        if len(cmd_line) < 3:
                            for option in self.cli_menu.current_context.selected[
                                "options"
                            ]:
                                if option.lower().startswith(
                                        word_before_cursor
                                ):
                                    yield Completion(option,
                                                     -len(word_before_cursor))
                        return

            if hasattr(self.cli_menu.current_context, "_cmd_registry"):
                for cmd in self.cli_menu.current_context._cmd_registry:
                    if cmd.startswith(word_before_cursor):
                        yield Completion(cmd, -len(word_before_cursor))

            for ctx in self.cli_menu.get_context():
                if ctx.name.startswith(word_before_cursor) and \
                        ctx.name is not self.cli_menu.current_context.name:
                    yield Completion(ctx.name, -len(word_before_cursor))

            if self.cli_menu.current_context.name != "main":
                for cmd in self.cli_menu._cmd_registry:
                    if cmd.startswith(word_before_cursor):
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
            HTML(f"[<ansiyellow>{len(self.teamservers.connections)}"
                 "</ansiyellow>] RL ≫ "),
            bottom_toolbar=functools.partial(bottom_toolbar,
                                             ts=self.teamservers),
            completer=self.completer,
            complete_in_thread=True,
            complete_while_typing=True,
            auto_suggest=AutoSuggestFromHistory(),
            search_ignore_case=True
        )
        # To avoid error in tab completion
        self.available = []

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
            (f"[<ansiyellow>{len(self.teamservers.connections)}</ansiyellow>]"
             f" RL (<ansired>{ctx.name}</ansired>){ctx.prompt or '' } ≫ ")
        )

    async def switched_context(self, text):
        for ctx in self.get_context():
            if self.teamservers.selected and \
                    self.teamservers.selected.stats.CONNECTED \
                    and ctx.name == "profiles":
                res = await self.teamservers.send(ctx=ctx.name,
                                                  cmd="list")
                if res and res.result:
                    ctx.profiles = [row[0] for row in res.result]
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
            cmd = shlex.split(text)
            logging.debug(f"command: {cmd[0]} args: {cmd[1:]} "
                          f"ctx: {self.current_context.name}")
            if cmd[0] == "aws":
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await proc.communicate()
                if stderr:
                    print(stderr.decode("utf-8"), end="")
                else:
                    print(stdout.decode("utf-8"), end="")
                return
            try:
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
                            getattr(self.current_context, cmd[0])(
                                args=args,
                                response=res
                            )
                    elif res.status == "error":
                        print_bad(res.result)
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
