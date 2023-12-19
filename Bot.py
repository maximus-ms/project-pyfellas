from Contacts import Contacts


class Bot:
    def __init__(self, contacts: Contacts):
        self.cmds = {}
        self.contacts = contacts
        contacts_cmds = self.contacts.help()
        for cmd in contacts_cmds:
            self.cmds[cmd[0]] = (self.contacts.exe, cmd[1:])

        # contacts_cmds = self.notes.help()

    def get_input(self):
        return "", ""

    def run(self):
        while True:
            cmd, args = self.get_input()
            res = self.cmds[cmd][0](args)
            print(res)

    def cmd_error_handle(self, cmd):
        return self.cmds[cmd][1]
