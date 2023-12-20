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
            "rename-contact",
            "rename-contact <Old_name> <New_ame>",
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
            "Edit email number of the contact",
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
    )


    def __init__(self) -> None:
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
        # ....

    def help(self):
        return Contacts.cmds_help

    def exe(self, cmd, args):
        return self.cmds[cmd](args)

    def add_contact(self, args):
        (name,) = args
        # TODO new_record = Record(Name(name).value)

        return f"Contact '{name}' was added."

    def rename_contact(self, args):
        # TODO 
        return "" 

    def delete_contact(self, args):
        # TODO 
        return "" 

    def add_phone(self, args):
        # TODO 
        return "" 

    def edit_phone(self, args):
        # TODO 
        return "" 

    def delete_phone(self, args):
        # TODO 
        return ""   
              
    def add_email(self, args):
        # TODO 
        return "" 

    def edit_email(self, args):
        # TODO 
        return "" 

    def delete_email(self, args):
        # TODO 
        return ""
        
    def add_birthday(self, args):
        # TODO 
        return "" 

    def edit_birthday(self, args):
        # TODO 
        return "" 

    def delete_birthday(self, args):
        # TODO 
        return ""     

    def add_address(self, args):
        # TODO 
        return "" 

    def edit_address(self, args):
        # TODO 
        return "" 

    def delete_address(self, args):
        # TODO 
        return ""  
