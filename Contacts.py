from collections import UserDict
from datetime import datetime
import re
from BaseClasses import *


class Name(Field):
    """Class for storing a contact's name. Mandatory field."""

    def validate(self, name: str):
        name = name.strip()
        parts = name.split()
        if len(parts) > 1:
            raise ErrorWithMsg("Name must be a single word")
        if type(name) is str and len(name) > 0:
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
    """Class for validation emails. Validate the format (Exa.maple@exam.ple)"""

    def validate(self, email):
        email = email.strip()
        try:
            result = re.match(
                r"\b[a-z]{1}[\w\.\-\_]+@[\w\.\-\_]+\.[a-z]{2,}", email.lower()
            ).group()
        except:
            raise ErrorWithMsg("Invalid email format")
        return result


class Contact:
    """Class for storing contact information, including name, phone, etc."""

    def __init__(self, name:Name, phone=Phone(), email=Email(), birthday=Birthday(), address=Address()):
        self.name = name
        self.phone = phone
        self.email = email
        self.birthday = birthday
        self.address = address

    def __str__(self):
        text = f"Name: {self.name}"
        if self.phone and self.phone.value:
            text += f", phone: {self.phone}"
        if self.email and self.email.value:
            text += f", e-mail: {self.email}"
        if self.birthday and self.birthday.value:
            text += f", birthday: {self.birthday}"
        if self.address and self.address.value:
            text += f", address: {self.address}"
        return text

    def set_all(self, name:str=None, phone:str=None, email:str=None, birthday:str=None, address:str=None):
        if not name is None:
            self.name = Name(name)
        if not phone is None:
            self.phone = Phone(phone)
        if not email is None:
            self.email = Email(email)
        if not birthday is None:
            self.birthday = Birthday(birthday)
        if not address is None:
            self.address = Address(address)

class Contacts(UserDict, CmdProvider):
    ERROR_MESSAGE_CONTACT_ALREADY_EXISTS = "Contact '{}' already exists"
    ERROR_MESSAGE_CONTACT_NOT_FOUND = "Contact is not found"
    ERROR_EMPTY_CONTACTS_LIST = "Contacts list is empty. Please add some contacts first"
    cmds_help = (
        ("add-contact", "add-contact", "Add contact to address book"),
        (
            "rename-contact",
            "rename-contact <Old_name> <New_name>",
            "Rename existing contact",
        ),
        (
            "delete-contact",
            "delete-contact <Name>",
            "Delete existing contact",
        ),
        (
            "add-phone",
            "add-phone <Name> <Phone_number>",
            "Add phone number to the contact",
        ),
        (
            "edit-phone",
            "edit-phone <Name> <New_number>",
            "Edit phone number of the contact",
        ),
        (
            "delete-phone",
            "delete-phone <Name>",
            "Delete phone number of the contact",
        ),
        (
            "add-email",
            "add-email <Name> <Email>",
            "Add email to the contact",
        ),
        (
            "edit-email",
            "edit-email <Name> <New_email>",
            "Edit email of the contact",
        ),
        (
            "delete-email",
            "delete-email <Name>",
            "Delete email of the contact",
        ),
        (
            "add-birthday",
            "add-birthday <Name> <Birthday>",
            "Add birthday to the contact",
        ),
        (
            "edit-birthday",
            "edit-birthday <Name> <New_birthday>",
            "Edit birthday of the contact",
        ),
        (
            "delete-birthday",
            "delete-birthday <Name>",
            "Delete birthday of the contact",
        ),
        (
            "add-address",
            "add-address <Name> <Address>",
            "Add address to the contact",
        ),
        (
            "edit-address",
            "edit-address <Name> <New_address>",
            "Edit address of the contact",
        ),
        (
            "delete-address",
            "delete-address <Name>",
            "Delete address of the contact",
        ),
        (   "all-contacts", "all-contacts", "Show the complete list of contacts")
    )

    def __init__(self) -> None:
        super().__init__()
        self.cmds = {}
        self.cmds["add-contact"] = self.add_contact
        self.cmds["rename-contact"] = self.rename_contact
        self.cmds["delete-contact"] = self.delete_contact
        self.cmds["add-phone"] = self.add_phone
        self.cmds["edit-phone"] = self.edit_phone
        self.cmds["delete-phone"] = self.delete_phone
        self.cmds["add-email"] = self.add_email
        self.cmds["edit-email"] = self.edit_email
        self.cmds["delete-email"] = self.delete_email
        self.cmds["add-birthday"] = self.add_birthday
        self.cmds["edit-birthday"] = self.edit_birthday
        self.cmds["delete-birthday"] = self.delete_birthday
        self.cmds["add-address"] = self.add_address
        self.cmds["edit-address"] = self.edit_address
        self.cmds["delete-address"] = self.delete_address
        self.cmds["all-contacts"] = self.all_contacts

    def __str__(self):
        return "\n".join(self.get_str_list_of_contacts())

    def get_str_list_of_contacts(self):
        if len(self.data) == 0:
            raise ErrorWithMsg(Contacts.ERROR_EMPTY_CONTACTS_LIST)
        return [str(note) for note in self.data.values()]

    def help(self):
        return Contacts.cmds_help

    def exe(self, cmd, args):
        return self.cmds[cmd](args)

    def assert_name_is_free(self, name):
        good_name = Name(name)
        if name in self.data:
            raise ErrorWithMsg(Contacts.ERROR_MESSAGE_CONTACT_ALREADY_EXISTS.format(name))
        pass

    def add_contact(self, args):
        if len(args) > 0:
            raise ValueError
        list_of_types = [Name, Phone, Email, Birthday, Address]
        list_of_prompts = ["Name: ", "Phone: ", "Email: ", "Birthday: ", "Address: "]
        data = get_extra_data_from_user(list_of_types, list_of_prompts, self.assert_name_is_free)
        name = data[0].value
        self.data[name] = Contact(data[0], data[1], data[2], data[3], data[4])
        return f"Contact '{name}' was added."

    def rename_contact(self, args):
        (name, new_name) = args
        good_name = Name(name)
        if not name in self.data:
            raise ErrorWithMsg(Contacts.ERROR_MESSAGE_CONTACT_NOT_FOUND)
        good_new_name = Name(new_name)
        if new_name in self.data:
            raise ErrorWithMsg(Contacts.ERROR_MESSAGE_CONTACT_ALREADY_EXISTS.format(new_name))
        contact = self.data.pop(name)
        contact.name = good_new_name
        self.data[new_name] = contact
        return f"Contact {name} was renamed to {new_name}"

    def delete_contact(self, args):
        # TODO
        return ""

    def add_phone(self, args):
        (name, phone) = args
        if not name in self.data:
            raise ErrorWithMsg(Contacts.ERROR_MESSAGE_CONTACT_NOT_FOUND)
        self.data[name].phone = Phone(phone)
        return "Phone {phone} was set for contact {name}"

    def edit_phone(self, args):
        return self.add_phone(args)

    def delete_phone(self, args):
        (name,) = args
        if not name in self.data:
            raise ErrorWithMsg(Contacts.ERROR_MESSAGE_CONTACT_NOT_FOUND)
        self.data[name].phone = None
        return "Phone was deleted from contact {name}"

    def add_email(self, args):
        # TODO
        return ""

    def edit_email(self, args):
        return self.add_email(args)

    def delete_email(self, args):
        # TODO
        return ""

    def add_birthday(self, args):
        # TODO
        return ""

    def edit_birthday(self, args):
        return self.add_birthday(args)

    def delete_birthday(self, args):
        # TODO
        return ""

    def add_address(self, args):
        # TODO
        return ""

    def edit_address(self, args):
        return self.add_address(args)

    def delete_address(self, args):
        # TODO
        return ""

    def all_contacts(self, args):
        return self.get_str_list_of_contacts()
