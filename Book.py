import pickle
from Contacts import Contacts
from Notes import Notes


class Book:
    """Class for contacts and notes"""

    def __init__(self, filename=None) -> None:
        self.contacts = Contacts()
        self.notes = Notes()
        self.filename = filename
        self.load_from_file()

    def load_from_file(self):
        try:
            with open(self.filename, "rb") as f:
                data = pickle.load(f)
                self.contact = data.get("contacts", Contacts())
                self.notes = data.get("notes", Notes())
        except:
            pass

    def save_to_file(self):
        data = {"contacts": self.contacts, "notes": self.notes}
        with open(self.filename, "wb") as f:
            pickle.dump(data, f)
