from abc import ABC, abstractmethod


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


class Topic(Field):
    """Topic field of Notes"""

    def validate(self, topic: str):
        if not topic:
            raise ErrorWithMsg("Topic cannot be empty.")
        return topic


class Text(Field):
    """Text field of Notes"""

    def validate(self, text: str):
        if not isinstance(text, str):
            raise ErrorWithMsg("Text must be a string.")
        return text


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
