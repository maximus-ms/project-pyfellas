from Contacts import Contacts


# from Notes import Notes
class Notes:
    def help(self):
        return []

    def exe(self, args):
        return ""


class Book:
    """Class for contacts and notes"""

    def __init__(self) -> None:
        self.contacts = Contacts()
        self.notes = Notes()
