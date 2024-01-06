from collections import defaultdict, OrderedDict
import platform
import requests
from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from rich.console import Text

from BaseClasses import *
from Contacts import Contacts, Name, Number, YesNo
from Notes import Notes


class CLI:
    COLOR_SCHEME = (
        (None, None, None, None, None, None),
        (None, "green", "magenta", "green", "red", "grey0"),
    )
    curr_color_scheme = 1
    MSG_STYLE_DEFAULT = None
    MSG_STYLE_WELCOME = "green"
    MSG_STYLE_PROMPT = "magenta"
    MSG_STYLE_OK = "green"
    MSG_STYLE_ERROR = "red"
    MSG_STYLE_HINT = "grey0"
    console = Console()
    print = console.print
    input = console.input

    def apply_color_scheme(ix):
        if ix >= len(CLI.COLOR_SCHEME):
            return
        CLI.curr_color_scheme = ix
        CLI.MSG_STYLE_DEFAULT = CLI.COLOR_SCHEME[ix][0]
        CLI.MSG_STYLE_WELCOME = CLI.COLOR_SCHEME[ix][1]
        CLI.MSG_STYLE_PROMPT = CLI.COLOR_SCHEME[ix][2]
        CLI.MSG_STYLE_OK = CLI.COLOR_SCHEME[ix][3]
        CLI.MSG_STYLE_ERROR = CLI.COLOR_SCHEME[ix][4]
        CLI.MSG_STYLE_HINT = CLI.COLOR_SCHEME[ix][5]

    def color_scheme_ix_valid(ix):
        if ix >= len(CLI.COLOR_SCHEME):
            raise ErrorWithMsg("Color theme should be in a range [0..1]")


class WordCompleter(Completer):
    def __init__(self, word_list):
        self.word_list = word_list

    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor()
        completions = []
        for word in self.word_list:
            if word.startswith(word_before_cursor):
                completions.append(
                    Completion(word, start_position=-len(word_before_cursor))
                )
                # Limit the number of suggestions
        return completions


class SettingsItem:
    def __init__(
        self, name=None, _type=str, checker=None, default=None
    ) -> None:
        self.name = name
        self.type = _type
        self.checker = checker
        self.value = default


class Settings:
    def __init__(self) -> None:
        self.data = {}
        self.order = []
        self.config = {}
        self.add_setting("Name", Name, None, "")
        self.add_setting("Show birthdays", YesNo, None, True)
        self.add_setting("Show reminders", YesNo, None, True)
        self.add_setting("Show quote", YesNo, None, True)
        self.add_setting(
            "Color theme",
            Number,
            CLI.color_scheme_ix_valid,
            CLI.curr_color_scheme,
        )
        self.add_setting("Use prompt", YesNo, None, True)

    def add_setting(self, name, _type, checker=None, default=None):
        self.data[name] = default
        self.config[name] = SettingsItem(name, _type, checker, default)
        self.order.append(name)


class CLIBot(CmdProvider, FrontBase):
    HELLO_MSG = "Hi{}, this is your assistant"
    HELLO_HELP_MSG = "write your command ('h|help' for details)"
    BYE_MSG = "Bye!"
    PROMPT_MSG = ">>> "
    INVALID_CMD_MSG = "Invalid command!"
    HELP_MESSAGE_HEAD = "\n List of supported commands:"
    HELP_MSG_CMDS_FORMAT = "    {:<25} : {}"
    PARSING_ERROR_MSG_CMDS_FORMAT = "{}\nExpected format: {}"
    SHOW_WELCOME_QUOTE = True

    SAVE_PATTERNS = ("add", "edit", "delete", "rename", "settings")

    __cmds_help = (
        ("quote", "quote", "Show random quote from https://zenquotes.io/"),
        ("help", "h|help", "Show this message"),
        ("h", "h|help", "Show this message"),
        ("settings", "settings", "Configure assistant"),
        ("exit", "q|exit|close", "Finish to work with an assistant"),
        ("close", "q|exit|close", "Finish to work with an assistant"),
        ("q", "q|exit|close", "Finish to work with an assistant"),
    )

    def __init__(self):
        self.save_handler = None
        self.name = ""
        self.use_prompt = True
        self.settings = Settings()
        self.apply_setting()
        self.__finish = False
        self.__is_error = False
        self.cmds = {
            "quote": self.show_quote,
            "help": self.get_help_message,
            "h": self.get_help_message,
            "settings": self.configure_assistant_by_user,
            "exit": self.exit,
            "close": self.exit,
            "q": self.exit,
        }

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

    def set_cmd_providers(self, cmd_providers):
        self.__list_of_cmds_providers = cmd_providers
        self.__update_exes_dict()
        all_cmds = sorted(list(self.__get_cmds_list()))
        self.cmd_completer = WordCompleter(all_cmds)

    def set_save_handler(self, handler):
        self.save_handler = handler

    def get_extra_data_from_user(
        self,
        list_of_types,
        list_of_prompts,
        assert_validator=None,
        mandatory_first_entry=True,
        mandatory_all_entries=False,
    ):
        num = min(len(list_of_types), len(list_of_prompts))
        data = [None] * num
        assert_validators = [None] * num
        if type(assert_validator) is list:
            assert_validators = assert_validator + assert_validators
        else:
            assert_validators[0] = assert_validator
        for i in range(num):
            is_current_entry_mandatory = (
                mandatory_first_entry or mandatory_all_entries
            )
            current_prompt = Text(
                list_of_prompts[i], style=CLI.MSG_STYLE_PROMPT
            )
            while True:
                user_data = ""
                try:
                    user_data = CLI.input(current_prompt)
                    user_data = user_data.strip()
                    if len(user_data) == 0 and (
                        not is_current_entry_mandatory
                    ):
                        break
                    good_data = list_of_types[i](user_data)
                    if assert_validators[i]:
                        assert_validators[i](good_data.value)
                    data[i] = list_of_types[i](user_data)
                    mandatory_first_entry = False
                    break
                except KeyboardInterrupt:
                    CLI.print()
                    if is_current_entry_mandatory:
                        raise ErrorWithMsg("Command was interrupted")
                    return data
                except ErrorWithMsg as er:
                    if len(user_data) == 0:
                        CLI.print(
                            "This field can not be empty",
                            style=CLI.MSG_STYLE_ERROR,
                            highlight=False,
                        )
                    else:
                        CLI.print(
                            er, style=CLI.MSG_STYLE_ERROR, highlight=False
                        )
        return data

    def get_for_file(self):
        return self.settings.data

    def set_from_file(self, data):
        self.settings.data = data
        self.apply_setting()

    def save_to_file(self):
        if not self.save_handler is None:
            self.save_handler()

    def apply_setting(self):
        if self.settings.data["Name"]:
            self.name = self.settings.data["Name"]
            if len(self.name) > 0:
                self.name = " " + self.name
        if not self.settings.data["Show birthdays"]:
            Contacts.WELCOME_BIRTHDAYS_NUM_OF_DAYS = 0
        if not self.settings.data["Show reminders"]:
            Notes.WELCOME_REMINDERS_NUM_OF_DAYS = 0
        if not self.settings.data["Show quote"] is None:
            CLIBot.SHOW_WELCOME_QUOTE = self.settings.data["Show quote"]
        if not self.settings.data["Color theme"] is None:
            CLI.apply_color_scheme(self.settings.data["Color theme"])
        if not self.settings.data["Use prompt"] is None:
            self.use_prompt = self.settings.data["Use prompt"]

    def configure_assistant_by_user(self, args):
        if len(args) > 0:
            raise ValueError
        list_of_types = []
        list_of_prompts = []
        list_of_asserts = []
        for item in self.settings.order:
            list_of_types.append(self.settings.config[item].type)
            if item == "Name":
                curr = (
                    f" (current {self.settings.data[item]})"
                    if self.settings.data[item]
                    else ""
                )
                list_of_prompts.append(f"{item} /'~' to delete/{curr} : ")
            else:
                list_of_prompts.append(
                    f"{item} (current {self.settings.data[item]}): "
                )
            list_of_asserts.append(self.settings.config[item].checker)
        data = self.get_extra_data_from_user(
            list_of_types,
            list_of_prompts,
            list_of_asserts,
            mandatory_first_entry=False,
        )
        cnt = 0
        for i, item in enumerate(self.settings.order):
            if data[i] is None:
                continue
            self.settings.data[item] = data[i].value
            cnt += 1
        if cnt == 0:
            raise ErrorWithMsg("No settings to apply")
        if self.settings.data["Name"] == "~":
            self.settings.data["Name"] = ""
        self.apply_setting()
        return "New settings applied"

    def help(self):
        return CLIBot.__cmds_help

    def exe(self, cmd, args, get_extra_data_from_user_handler):
        return self.cmds[cmd](args)

    def get_quote(self):
        response = requests.get("https://zenquotes.io/api/random").json()
        q = response[0]["q"]
        a = response[0]["a"]
        random_quote = f'"{q}" - {a} (https://zenquotes.io/)'
        return random_quote

    def welcome_message(self):
        if CLIBot.SHOW_WELCOME_QUOTE:
            return f"Quote for today: {self.get_quote()}"
        else:
            return ""

    def show_quote(self, args):
        if len(args) > 0:
            raise ValueError
        return self.get_quote()

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
                return CLIBot.PARSING_ERROR_MSG_CMDS_FORMAT.format(
                    CLIBot.INVALID_CMD_MSG,
                    __self.exes[func.__name__.replace("_", "-")][1],
                )
            except Exception as e:
                return str(e)

        return inner

    def __unknown_cmd(self, cmd, args):
        raise ErrorWithMsg(CLIBot.INVALID_CMD_MSG)

    def exit(self, args):
        self.__finish = True
        return CLIBot.BYE_MSG

    def get_help_message(self, args):
        help_dict = OrderedDict()
        for cmd_provider in self.__list_of_cmds_providers:
            help = cmd_provider.help()
            for l in help:
                help_dict[l[1]] = l[2]
        txt_list = list()
        txt_list.append(CLIBot.HELP_MESSAGE_HEAD)
        for h1, h2 in help_dict.items():
            txt_list.append(CLIBot.HELP_MSG_CMDS_FORMAT.format(h1, h2))
        txt_list.append("")
        return txt_list

    def exe_cmd(self, cmd, args):
        try:
            self.__is_error = True
            ret = self.exes[cmd][0](cmd, args, self.get_extra_data_from_user)
            self.__is_error = False
            return ret
        except ErrorWithMsg as e:
            return e
        except ValueError as e:
            return CLIBot.PARSING_ERROR_MSG_CMDS_FORMAT.format(
                CLIBot.INVALID_CMD_MSG, self.exes[cmd.replace("_", "-")][1]
            )
        except Exception as e:
            return str(e)

    def cmd_input(self, msg, style=CLI.MSG_STYLE_DEFAULT):
        if "Darwin" == platform.system():
            self.use_prompt = False
        if self.use_prompt:
            user_input = prompt(
                msg, completer=self.cmd_completer, reserve_space_for_menu=5
            )
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

    def save_if_cmd(self, cmd):
        for p in CLIBot.SAVE_PATTERNS:
            if p in cmd:
                self.save_to_file()
                return

    def run(self):
        CLI.print(
            CLIBot.HELLO_MSG.format(self.name),
            style=CLI.MSG_STYLE_WELCOME,
            highlight=False,
        )
        for member in self.__list_of_cmds_providers:
            message = member.welcome_message()
            if message:
                CLI.print(
                    f"  {message}",
                    style=CLI.MSG_STYLE_WELCOME,
                    highlight=False,
                )

        CLI.print(
            CLIBot.HELLO_HELP_MSG, style=CLI.MSG_STYLE_HINT, highlight=False
        )

        try:
            while not self.__finish:
                try:
                    self.__is_error = False
                    cmd, args = self.get_input(
                        CLIBot.PROMPT_MSG, style=CLI.MSG_STYLE_PROMPT
                    )
                    if "__empty__" == cmd:
                        CLI.print(
                            CLIBot.HELLO_HELP_MSG,
                            style=CLI.MSG_STYLE_HINT,
                            highlight=False,
                        )
                    else:
                        res = self.exe_cmd(cmd, args)
                        if self.__is_error:
                            style = CLI.MSG_STYLE_ERROR
                        else:
                            style = CLI.MSG_STYLE_OK
                        CLIBot.print_all(res, style=style)
                        self.save_if_cmd(cmd)
                except KeyboardInterrupt:
                    CLIBot.print_all(CLIBot.BYE_MSG, style=CLI.MSG_STYLE_OK)
                    self.__finish = True

        except Exception as e:
            pass

        self.save_to_file()
