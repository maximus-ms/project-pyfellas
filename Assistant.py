import pickle
from pathlib import Path
from CLIBot import CLIBot
from Contacts import Contacts
from Notes import Notes


class Assistant:
    def __init__(self, filename: str) -> None:
        self.filename = Path(__file__).parent / filename
        self.front_list = ["cli_bot"]
        self.items = {
            "cli_bot": CLIBot(),
            "contacts": Contacts(),
            "notes": Notes(),
        }
        self.load_from_file()
        items = self.items.values()

        for i in self.front_list:
            self.items[i].set_cmd_providers(items)
            self.items[i].set_save_handler(self.save_to_file)

    def load_from_file(self):
        try:
            with open(self.filename, "rb") as f:
                data = pickle.load(f)
                for d in data:
                    if d in self.items:
                        self.items[d].set_from_file(data[d])
        except:
            pass

    def save_to_file(self):
        # TODO: add lock mechanism for multi-frontend case
        data = {}
        for d in self.items:
            data[d] = self.items[d].get_for_file()
        with open(self.filename, "wb") as f:
            pickle.dump(data, f)

    def run(self, front_name="cli_bot"):
        if front_name == "all":
            print("#TODO: implement run all frontends in different threads")
            return False

        if not front_name in self.front_list:
            print(f'ERROR: Can not find frontend "{front_name}"')
            return False

        self.items[self.front_list[0]].run()

        return True
