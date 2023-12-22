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


class Number(Field):
    """Class for validating number. Mandatory field."""

    def validate(self, number: str):
        try:
            value = int(number)
        except:
            raise ErrorWithMsg("Must be a number")
        return value


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

    def __init__(self, name: Name, phone=Phone(), email=Email(), birthday=Birthday(), address=Address()):
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

    def set_all(self, name: str = None, phone: str = None, email: str = None, birthday: str = None,
                address: str = None):
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
    ERROR_MESSAGE_CONTACT_NOT_FOUND = "Contact '{}' is not found"
    ERROR_EMPTY_CONTACTS_LIST = "Contacts list is empty. Please add some contacts first"
    WELCOME_BIRTHDAYS_NUM_OF_DAYS = 7
    BIRTHDAYS_NUM_OF_DAYS = 7
    cmds_help = (
        ("add-contact", "add-contact", "Add contact to address book"),
        ("rename-contact", "rename-contact", "Rename existing contact"),
        ("delete-contact", "delete-contact", "Delete existing contact"),
        ("add-phone", "add-phone", "Add phone number to the contact"),
        ("edit-phone", "edit-phone", "Edit phone number of the contact"),
        ("delete-phone", "delete-phone", "Delete phone number of the contact"),
        ("add-email", "add-email ", "Add email to the contact"),
        ("edit-email", "edit-email", "Edit email of the contact"),
        ("delete-email", "delete-email", "Delete email of the contact"),
        ("add-birthday", "add-birthday", "Add birthday to the contact"),
        ("edit-birthday", "edit-birthday", "Edit birthday of the contact"),
        ("delete-birthday", "delete-birthday", "Delete birthday of the contact"),
        ("add-address", "add-address", "Add address to the contact"),
        ("edit-address", "edit-address", "Edit address of the contact"),
        ("delete-address", "delete-address", "Delete address of the contact"),
        ("find-contact", "find-contact", "Find a contact in the address book"),
        ("find-phone", "find-phone", "Find a phone in the address book"),
        ("find-email", "find-email", "Find an email in the address book"),
        ("find-birthday", "find-birthday", "Find a birthday in the address book"),
        ("find-address", "find-address", "Find an address in the address book"),
        ("birthdays", "birthdays", "Show birthdays for next X days"),
        ("all-contacts", "all-contacts", "Show list of contacts"),
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
        self.cmds["find-contact"] = self.find_contact
        self.cmds["find-phone"] = self.find_phone
        self.cmds["find-email"] = self.find_email
        self.cmds["find-birthday"] = self.find_birthday
        self.cmds["find-address"] = self.address
        self.cmds["birthdays"] = self.birthdays
        self.cmds["all-contacts"] = self.all_contacts

    def __str__(self):
        return "\n".join(self.get_str_list_of_contacts())

    def welcome_message(self):
        bd_contacts = self.__birthdays(Contacts.WELCOME_BIRTHDAYS_NUM_OF_DAYS)
        num = 0
        for contact in bd_contacts:
            if "Name" in contact:
                num += 1
        if num > 0:
            return f"You have {num} birthday(s) during next {Contacts.WELCOME_BIRTHDAYS_NUM_OF_DAYS} day(s)"
        else:
            return ""

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

    def assert_name_exist(self, name):
        good_name = Name(name)
        if not name in self.data:
            raise ErrorWithMsg(Contacts.ERROR_MESSAGE_CONTACT_NOT_FOUND.format(name))
        pass

    def add_contact(self, args):
        if len(args) > 0:
            raise ValueError
        list_of_types = [Name, Phone, Email, Birthday, Address]
        list_of_prompts = ["Name: ", "Phone: ", "Email: ", "Birthday: ", "Address: "]
        data = get_extra_data_from_user(list_of_types, list_of_prompts, self.assert_name_is_free)
        name = data[0].value
        self.data[name] = Contact(data[0], data[1], data[2], data[3], data[4])
        return f"Contact '{name}' was added"

    def rename_contact(self, args):
        if len(args) > 0:
            raise ValueError
        list_of_types = [Name, Name]
        list_of_prompts = ["Old name: ", "New name: "]
        list_of_asserts = [self.assert_name_exist, self.assert_name_is_free]
        data = get_extra_data_from_user(list_of_types, list_of_prompts, list_of_asserts, mandatory_all_entries=True)
        old_name = data[0].value
        new_name = data[1].value
        contact = self.data.pop(old_name)
        contact.name = new_name
        self.data[new_name] = contact
        return f"Contact '{old_name}' was renamed to '{new_name}'"

    def delete_contact(self, args):  # DONE
        if len(args) > 0:
            raise ValueError
        list_of_types = [Name]
        list_of_prompts = ["Name: "]
        data = get_extra_data_from_user(list_of_types, list_of_prompts, self.assert_name_exist)
        name = data[0].value
        self.data.pop(name)
        return f"Contact '{name}' was deleted"

    def add_phone(self, args):
        if len(args) > 0:
            raise ValueError
        list_of_types = [Name, Phone]
        list_of_prompts = ["Name: ", "Phone: "]
        data = get_extra_data_from_user(list_of_types, list_of_prompts, self.assert_name_exist,
                                        mandatory_all_entries=True)
        name = data[0].value
        self.data[name].phone = data[1]
        return f"Phone for '{name}' was set"

    def edit_phone(self, args):
        return self.add_phone(args)

    def delete_phone(self, args):
        if len(args) > 0:
            raise ValueError
        list_of_types = [Name]
        list_of_prompts = ["Name: "]
        data = get_extra_data_from_user(list_of_types, list_of_prompts, self.assert_name_exist)
        name = data[0].value
        self.data[name].phone = None
        return f"Phone for '{name}' was deleted"

    def add_email(self, args):
        if len(args) > 0:
            raise ValueError
        list_of_types = [Name, Email]
        list_of_prompts = ["Name: ", "Email: "]
        data = get_extra_data_from_user(list_of_types, list_of_prompts, self.assert_name_exist,
                                        mandatory_all_entries=True)
        name = data[0].value
        self.data[name].email = data[1]
        return f"Email for '{name}' was set"

    def edit_email(self, args):
        return self.add_email(args)

    def delete_email(self, args):
        if len(args) > 0:
            raise ValueError
        list_of_types = [Name]
        list_of_prompts = ["Name: "]
        data = get_extra_data_from_user(list_of_types, list_of_prompts, self.assert_name_exist)
        name = data[0].value
        self.data[name].email = None
        return f"Email for '{name}' was deleted"

    def add_birthday(self, args):
        if len(args) > 0:
            raise ValueError
        list_of_types = [Name, Birthday]
        list_of_prompts = ["Name: ", "Birthday: "]
        data = get_extra_data_from_user(list_of_types, list_of_prompts, self.assert_name_exist,
                                        mandatory_all_entries=True)
        name = data[0].value
        self.data[name].birthday = data[1]
        return f"Birthday for '{name}' was set"

    def edit_birthday(self, args):
        return self.add_birthday(args)

    def delete_birthday(self, args):
        if len(args) > 0:
            raise ValueError
        list_of_types = [Name]
        list_of_prompts = ["Name: "]
        data = get_extra_data_from_user(list_of_types, list_of_prompts, self.assert_name_exist,
                                        mandatory_all_entries=True)
        name = data[0].value
        self.data[name].birthday = None
        return f"Birthday for '{name}' was deleted"

    def add_address(self, args):
        if len(args) > 0:
            raise ValueError
        list_of_types = [Name, Address]
        list_of_prompts = ["Name: ", "Address: "]
        data = get_extra_data_from_user(list_of_types, list_of_prompts, self.assert_name_exist,
                                        mandatory_all_entries=True)
        name = data[0].value
        self.data[name].address = data[1]
        return f"Address for '{name}' was set"

    def edit_address(self, args):
        return self.add_address(args)

    def delete_address(self, args):
        if len(args) > 0:
            raise ValueError
        list_of_types = [Name]
        list_of_prompts = ["Name: "]
        data = get_extra_data_from_user(list_of_types, list_of_prompts, self.assert_name_exist,
                                        mandatory_all_entries=True)
        name = data[0].value
        self.data[name].address = None
        return f"Address for '{name}' was deleted"

    def find_contact(self, args):
        if len(args) > 0:
            raise ValueError
        list_of_types = [Name]
        list_of_prompts = ["Name: "]
        data = get_extra_data_from_user(list_of_types, list_of_prompts, self.assert_name_exist)
        return str(self.data[data[0].value])

    def find_phone(self, args):
        if len(args) > 0:
            raise ValueError
        list_of_types = [Phone]
        list_of_prompts = ["Phone: "]
        data = get_extra_data_from_user(list_of_types, list_of_prompts)
        phone = data[0]
        contact_list = [str(c) for c in self.data.values() if c.phone == phone]
        if len(contact_list) == 0:
            raise ErrorWithMsg("Phone is not found")
        return contact_list

    def find_email(self, args):
        # TODO
        return "TODO find_email"

    def find_birthday(self, args):
        # TODO
        return "TODO find_birthday"

    def address(self, args):
        # TODO
        return "TODO address"

    def all_contacts(self, args):
        return self.get_str_list_of_contacts()

    def repack_birthdays_for_search(self):
        birthday_list = []
        for contact in self.data.values():
            if contact.birthday:
                entry = {
                    "text": str(contact),
                    "event": datetime.strptime(contact.birthday.value, "%d.%m.%Y"),
                }
                birthday_list.append(entry)
        return birthday_list

    def __birthdays(self, num_of_days):
        res_birthday_list = []
        if num_of_days > 0:
            birthday_list = self.repack_birthdays_for_search()
            res_birthday_list = get_entries_for_next_x_days(birthday_list, num_of_days)
        return res_birthday_list

    def birthdays(self, args):
        num_of_days = Contacts.BIRTHDAYS_NUM_OF_DAYS
        if len(args) > 0:
            raise ValueError
        list_of_types = [Number]
        list_of_prompts = [f"Days (default {num_of_days}): "]
        data = get_extra_data_from_user(list_of_types, list_of_prompts, mandatory_first_entry=False)
        if not data[0] is None:
            num_of_days = data[0].value
        res_birthday_list = self.__birthdays(num_of_days)
        if len(res_birthday_list) == 0:
            return f"No birthdays for next {num_of_days} days"
        return res_birthday_list
