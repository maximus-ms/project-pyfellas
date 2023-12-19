from BaseClasses import Field, ErrorWithMsg
from datetime import datetime


class Name(Field):
    """Class for storing a contact's name. Mandatory field."""

    def validate(self, name: str):
        name = name.strip()
        # TODO len(name) > 0
        if type(name) is str:
            return name
        raise ErrorWithMsg("Name must be a string")


class Phone(Field):
    """Class for storing a phone number. Validates the format (10 digits)."""

    def validate(self, number: str):
        number = number.strip()
        if len(number) == 10 and number.isdigit():
            return number
        raise ErrorWithMsg("Invalid phone number format (expecting 10 digits)")


class Birthday(Field):
    """Class for storing a birthday. Validates the format (expecting DD.MM.YYYY)."""

    def validate(self, birthday: str):
        birthday = birthday.strip()
        try:
            datetime.strptime(birthday, "%d.%m.%Y")
        except:
            raise ErrorWithMsg("Invalid birthday format (DD.MM.YYYY)")
        return birthday


class Contacts:
    cmds = [
        ["add-contact", "add-contact <Name>", "Add contact to address book"],
        [
            "add-phone",
            "add-phone <Name> <phone_number>",
            "Add phone number to the contact",
        ],
        [
            "edit-contact",
            "edit-contact <old_name> <new_ame>",
            "Rename existing contact",
        ],
        ["contact-hello", "contact-hello", "contact-hello"],
    ]

    def __init__(self) -> None:
        pass

    def help(self):
        return Contacts.cmds

    def exe(self, cmd, args):
        return self.cmds[cmd](args)

    def add_contact(self, args):
        (name,) = args
        # TODO new_record = Record(Name(name).value)

        return f"Contact '{name}' was added."

    def edit_contact(self, args):
        pass
        return ""

    def add_phone(self, args):
        (name, in_phone) = args
        # TODO self.contacts[Name(name).value].phone = Phone(in_phone)

        return f"Contact '{name}' was added."

    def print_hello(self, args):
        if len(args) > 0:
            raise ValueError
        return "Hello!"
