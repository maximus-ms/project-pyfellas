from abc import ABC, abstractmethod
from rich.console import Console, Text

class CLI:
    MSG_STYLE_DEFAULT = None
    MSG_STYLE_WELCOME = "green"
    MSG_STYLE_PROMPT = "magenta"
    MSG_STYLE_OK = "green"
    MSG_STYLE_ERROR = "red"
    MSG_STYLE_HINT = "grey0"
    console = Console()
    print = console.print
    input = console.input


def get_extra_data_from_user(list_of_types, list_of_prompts, assert_validator=None, mandatory_first_entry=True):
    first_entry = True
    num = min(len(list_of_types), len(list_of_prompts))
    data = [None] * num
    for i in range(num):
        current_prompt = Text(list_of_prompts[i], style=CLI.MSG_STYLE_PROMPT)
        while True:
            user_data = ""
            try:
                user_data = CLI.input(current_prompt)
                user_data = user_data.strip()
                if len(user_data) == 0:
                    if not (first_entry and mandatory_first_entry):
                        break
                if first_entry:
                    good_data = list_of_types[i](user_data)
                    if assert_validator:
                        assert_validator(good_data.value)
                data[i] = list_of_types[i](user_data)
                first_entry = False
                break
            except KeyboardInterrupt:
                CLI.print()
                return data
            except ErrorWithMsg as er:
                if first_entry and len(user_data) == 0:
                    CLI.print("Mandatory field cannot be empty", style=CLI.MSG_STYLE_ERROR, highlight=False)
                else:
                    CLI.print(er, style=CLI.MSG_STYLE_ERROR, highlight=False)
    return data


class ErrorWithMsg(Exception):
    pass


class Field(ABC):
    """Base class for every field"""

    def __init__(self, value=None):
        self.__value = None
        if not value is None:
            self.value = value

    def __str__(self):
        return self.value

    def __eq__(self, other):
        if type(other) is Field:
            return self.__value == other.value
        if type(other) is str:
            return self.__value == other
        return False

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value):
        self.__value = self.validate(new_value)

    @abstractmethod
    def validate(self, value) -> None:
        """Must raise an exception if not valid or return a value"""
        raise ErrorWithMsg("Unknown value validator")


class CmdProvider(ABC):
    #   __cmds_help_example = (
    #        ("cmd1", "cmd1 <arg>",          "cmd1 is used to call cmd1"),
    #        ("cmd2", "cmd1 <arg1>, <arg2>", "cmd2 is used to call cmd2"),
    #   )

    @abstractmethod
    def exe(self, cmd, args):
        raise ErrorWithMsg("Unknown exe()")
        # if cmd == "cmd1":
        # return self.cmd1(args)

    @abstractmethod
    def help(self):
        raise ErrorWithMsg("Unknown help()")
        return []
        # return _Your_class_name_.__cmds_example
