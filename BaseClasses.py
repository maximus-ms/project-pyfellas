from collections import UserDict
from abc import ABC, abstractmethod
from datetime import datetime


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
