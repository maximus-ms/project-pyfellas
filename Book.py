from BaseClasses import *
from Contacts import Contacts


# from Notes import Notes
class Notes(CmdProvider):
    def help(self):
        return []

    def exe(self, args):
        return ""


class Book:
    """Class for contacts and notes"""

    def __init__(self, filename=None) -> None:
        self.contacts = Contacts()
        self.notes = Notes()
        self.filename = filename
        self.load_from_file()

    def load_from_file(self):
        # TODO
        pass

    def save_to_file(self):
        # TODO
        pass
