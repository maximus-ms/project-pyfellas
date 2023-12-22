from Contacts import Contacts
from Notes import Notes


class Book:
    """Class for contacts and notes"""

    def __init__(self) -> None:
        self.contacts = Contacts()
        self.notes = Notes()
