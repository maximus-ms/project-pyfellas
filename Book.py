from BaseClasses import *
from Contacts import Contacts
import pickle

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
        with open(self.filename, "rb") as f:
            data = pickle.load(f)
            self.contact = data.get("contacts", {})
            self.notes = data.get("notes", {})
        pass

    def save_to_file(self):
        data = {"contacts": self.contacts, "notes": self.notes}
        with open(self.filename, "wb") as f:
                pickle.dump(data, f)