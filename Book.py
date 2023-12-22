import os
import pickle
from pathlib import Path
from Contacts import Contacts
from Notes import Notes


class Book:
    """Class for contacts and notes"""

    def __init__(self, filename=None) -> None:
        self.contacts = Contacts()
        self.notes = Notes()
        self.filename = Path(__file__).parent / filename
        self.load_from_file()

    def load_from_file(self):
        try:
            with open(self.filename, "rb") as f:
                data = pickle.load(f)
                self.contacts.data = data.get("contacts", Contacts())
                self.notes.data = data.get("notes", Notes())
        except:
            pass

    def save_to_file(self):
        data = {"contacts": self.contacts.data, "notes": self.notes.data}
        with open(self.filename, "wb") as f:
            pickle.dump(data, f)
