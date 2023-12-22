from collections import defaultdict, OrderedDict
import platform
from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from rich.console import Text

from BaseClasses import *
from Book import Book

class WordCompleter(Completer):
    def __init__(self, word_list):
        self.word_list = word_list

    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor()
        completions = []
        for word in self.word_list:
            if word.startswith(word_before_cursor):
                completions.append(Completion(word, start_position=-len(word_before_cursor)))
                # Limit the number of suggestions
        return completions


class Bot(CmdProvider):
    HELLO_MSG = "Hi, this is your assistant"
    HELLO_HELP_MSG = "write your command ('h|help' for details)"
    BYE_MSG = "Bye!"
    PROMPT_MSG = ">>> "
    INVALID_CMD_MSG = "Invalid command!"
    HELP_MESSAGE_HEAD = "\n List of supported commands:"
    HELP_MSG_CMDS_FORMAT = "    {:<25} : {}"
    PARSING_ERROR_MSG_CMDS_FORMAT = "{}\nExpected format: {}"
    SHOW_WELCOME_QUOTE = True

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
        all_cmds = sorted(list(self.__get_cmds_list()))
        self.cmd_completer = WordCompleter(all_cmds)

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

    def __get_cmds_list(self):
        return self.exes.keys()

    def help(self):
        return Bot.__cmds_help

    def exe(self, cmd, args):
        return self.cmds[cmd](args)

    def welcome_message(self):
        if Bot.SHOW_WELCOME_QUOTE:
            import requests
            response = requests.get("https://zenquotes.io/api/random").json()
            q = response[0]['q']
            a = response[0]['a']
            random_quote = f'Quote for today: "{q}" - {a} (https://zenquotes.io/)'
            return random_quote
        else:
            return ""

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
        return Bot.BYE_MSG

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
        return txt_list

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
        #TODO enable this exception catch
        # except Exception as e:
        #     return str(e)

    def cmd_input(self, msg, style=CLI.MSG_STYLE_DEFAULT, use_prompt=True):
        if 'Darwin' == platform.system():
            use_prompt = False
        if use_prompt:
            user_input = prompt(msg, completer=self.cmd_completer, reserve_space_for_menu=5)
        else:
            formatted_msg = Text(msg, style=style)
            user_input = CLI.input(formatted_msg)
        return user_input

    def get_input(self, message, style=CLI.MSG_STYLE_DEFAULT):
        try:
            user_input = self.cmd_input(message, style)
            cmd, *args = user_input.split()
            ret = cmd.strip().lower(), args
        except Exception as e:
            self.__is_error = True
            ret = "__empty__", (None,)
        return ret

    def print_all(data, style=None):
        if not isinstance(data, (list, tuple)):
            CLI.print(str(data), style=style, highlight=False)
            return
        # will print in chunks
        chunk_size = CLI.console.height - 1
        data_parts = [
            data[x : x + chunk_size] for x in range(0, len(data), chunk_size)
        ]
        prompt = Text(
            "-- press enter for more lines ('q' or ctrl+c to skip) --",
            style=CLI.MSG_STYLE_HINT,
        )
        index = 0
        try:
            for part in data_parts:
                CLI.print("\n".join(part), style=style, highlight=False)
                index += chunk_size
                if index >= len(data):
                    break
                in_data = CLI.input(prompt)
                if in_data.lower() == "q":
                    break
        except:
            CLI.print()
            pass

    def run(self):
        CLI.print(Bot.HELLO_MSG, style=CLI.MSG_STYLE_WELCOME, highlight=False)
        for member in self.__list_of_cmds_providers:
            message = member.welcome_message()
            if message:
                CLI.print(f"  {message}", style=CLI.MSG_STYLE_WELCOME, highlight=False)

        CLI.print(Bot.HELLO_HELP_MSG, style=CLI.MSG_STYLE_HINT, highlight=False)

        #TODO
        try:
            while not self.__finish:
                try:
                    self.__is_error = False
                    cmd, args = self.get_input(Bot.PROMPT_MSG, style=CLI.MSG_STYLE_PROMPT)
                    if "__empty__" == cmd:
                        CLI.print(Bot.HELLO_HELP_MSG, style=CLI.MSG_STYLE_HINT, highlight=False)
                    else:
                        res = self.exe_cmd(cmd, args)
                        if self.__is_error:
                            style = CLI.MSG_STYLE_ERROR
                        else:
                            style = CLI.MSG_STYLE_OK
                        Bot.print_all(res, style=style)
                except KeyboardInterrupt:
                    Bot.print_all(Bot.BYE_MSG, style=CLI.MSG_STYLE_OK)
                    self.__finish = True
        #TODO
        except KeyboardInterrupt as e:
        # except Exception as e:
            #TODO delete this print
            print(e)
            pass

        self.book.save_to_file()
