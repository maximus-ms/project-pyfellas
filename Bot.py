from collections import defaultdict, OrderedDict
from BaseClasses import *
from Book import Book

from rich.console import Console, Text


class Bot(CmdProvider):
    HELLO_MSG = "Hi, this is your assistant."
    PROMPT_MSG = ">>> "
    INVALID_CMD_MSG = "Invalid command!"
    HELP_MESSAGE_HEAD = "\n List of supported commands:"
    HELP_MSG_CMDS_FORMAT = "    {:<35} : {}"
    PARSING_ERROR_MSG_CMDS_FORMAT = "{}\nExpected format: {}"
    MSG_STYLE_DEFAULT = None
    MSG_STYLE_ERROR = "red"
    MSG_STYLE_OK = "dark_blue"

    __cmds_help = (
        ("help", "h|help", "Show this message."),
        ("h", "h|help", "Show this message."),
        ("exit", "q|exit|close", "Finish to work with an assistant."),
        ("close", "q|exit|close", "Finish to work with an assistant."),
        ("q", "q|exit|close", "Finish to work with an assistant."),
    )

    def __init__(self, book: Book):
        self.__finish = False
        self.__is_error = False
        self.console = Console()
        self.cmds = {
            "help": self.get_help_message,
            "h": self.get_help_message,
            "exit": self.exit,
            "close": self.exit,
            "q": self.exit,
        }
        self.book = book
        self.__list_of_cmds_providers = [
            self.book.contacts,
            self.book.notes,
            self,
        ]
        self.__update_exes_dict()

    def __add_exes(self, cmds_help, exe_handler):
        for cmd_help in cmds_help:
            cmd_txt = cmd_help[0]
            if cmd_txt in self.exes.keys():
                raise Exception(f"Command duplication: {cmd_txt}")
            self.exes[cmd_txt] = tuple([exe_handler] + list(cmd_help[1:]))

    def __update_exes_dict(self):
        self.exes = defaultdict(lambda: [self.__unknown_cmd, "", ""])
        for cmds_provider in self.__list_of_cmds_providers:
            self.__add_exes(cmds_provider.help(), cmds_provider.exe)

    def help(self):
        return Bot.__cmds_help

    def exe(self, cmd, args):
        return self.cmds[cmd](args)

    def cmd_errors(func):
        def inner(*args, **kwargs):
            try:
                __self = args[0]
                __self.__is_error = True
                ret = func(*args, **kwargs)
                __self.__is_error = False
                return ret
            except ErrorWithMsg as e:
                return e
            except ValueError as e:
                return Bot.PARSING_ERROR_MSG_CMDS_FORMAT.format(
                    Bot.INVALID_CMD_MSG,
                    __self.exes[func.__name__.replace("_", "-")][1],
                )
            except Exception as e:
                return str(e)

        return inner

    def __unknown_cmd(self, cmd, args):
        raise ErrorWithMsg(Bot.INVALID_CMD_MSG)

    def exit(self, args):
        self.__finish = True
        return "Bye!"

    def get_help_message(self, args):
        help_dict = OrderedDict()
        for cmd_provider in self.__list_of_cmds_providers:
            help = cmd_provider.help()
            for l in help:
                help_dict[l[1]] = l[2]
        txt_list = list()
        txt_list.append(Bot.HELP_MESSAGE_HEAD)
        for h1, h2 in help_dict.items():
            txt_list.append(Bot.HELP_MSG_CMDS_FORMAT.format(h1, h2))
        txt_list.append("")
        return "\n".join(txt_list)

    def exe_cmd(self, cmd, args):
        try:
            self.__is_error = True
            ret = self.exes[cmd][0](cmd, args)
            self.__is_error = False
            return ret
        except ErrorWithMsg as e:
            return e
        except ValueError as e:
            return Bot.PARSING_ERROR_MSG_CMDS_FORMAT.format(
                Bot.INVALID_CMD_MSG, self.exes[cmd.replace("_", "-")][1]
            )
        except Exception as e:
            return str(e)

    def get_input(self, message):
        try:
            user_input = input(message)
            cmd, *args = user_input.split()
            ret = cmd.strip().lower(), args
        except:
            self.__is_error = True
            ret = "__unknown_cmd", (None,)
        return ret

    def run(self):
        self.console.print(Bot.HELLO_MSG, style="bold green")
        while not self.__finish:
            self.__is_error = False
            cmd, args = self.get_input(Bot.PROMPT_MSG)
            res = self.exe_cmd(cmd, args)
            if self.__is_error:
                style = Bot.MSG_STYLE_ERROR
            else:
                style = Bot.MSG_STYLE_OK
            self.console.print(res, style=style)

        self.book.save_to_file()
