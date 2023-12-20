from BaseClasses import *
from datetime import datetime
import re

class Name(Field):
    """Class for storing a contact's name. Mandatory field."""

    def validate(self, name: str):
        name = name.strip()
        if type(name) is str and len(name) > 0:
            pass
        elif type(name) is str:
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

class Address(Field):
    """Class for Contact`s Address validation and storing"""

    def validate(self, address):
        address = address.strip()
        return address
    
class Email(Field):
    """Class for validation emails. Validate the format (Exa.maple@exam.ple) """

    def validate(self, email):
        email = email.strip()
        try:
            result = re.match(r'\b[a-z]{1}[\w\.\-\_]+@[\w\.\-\_]+\.[a-z]{2,}', email.lower()).group()
        except: 
            raise ErrorWithMsg("Invalid email format")
        return result 


class Contacts(CmdProvider):
    cmds_help = (
        ("add-contact", "add-contact <Name>", "Add contact to address book"),
        (
            "add-phone",
            "add-phone <Name> <phone_number>",
            "Add phone number to the contact",
        ),
        (
            "edit-contact",
            "edit-contact <old_name> <new_ame>",
            "Rename existing contact",
        ),
    )

    def __init__(self) -> None:
        self.cmds = {}
        self.cmds["add-contact"] = self.add_contact
        self.cmds["add-phone"] = self.add_phone
        self.cmds["edit-contact"] = self.edit_contact
        # ....

    def help(self):
        return Contacts.cmds_help

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
