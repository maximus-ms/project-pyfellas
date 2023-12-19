from collections import defaultdict

from Book import Book


class Bot:
    INVALID_CMD_MSG = "Invalid command!"
    HELP_MESSAGE_HEAD = "\nThis is a CLI Bot-assistant for a phone-book.\nList of supported commands:\n"

    def __init__(self, book: Book):
        self.book = book
        self.__update_cmds_dict()

    def __add_cmds(self, cmds, exe_handler):
        for cmd in cmds:
            cmd_txt = cmd[0]
            if cmd_txt in self.cmds.keys():
                raise Exception(f"Command duplication: {cmd_txt}")
            self.cmds[cmd_txt] = [exe_handler] + cmd[1:]

    def __update_cmds_dict(self):
        self.cmds = defaultdict(lambda : [self.__unknown_cmd, "", ""])
        self.__add_cmds(self.book.contacts.help(), self.book.contacts.exe)
        self.__add_cmds(self.book.notes.help(), self.book.notes.exe)

    def __unknown_cmd(self, args):
        return Bot.INVALID_CMD_MSG

    def exit(self, args):
        return "Bye!"

    def help(self, args):
        return "Bye!"

    def get_input(self, message):
        user_input = input(message)
        cmd, *args = user_input.split()
        ret = cmd.strip().lower(), args
        return ret

    def run(self):
        while True:
            cmd, args = self.get_input(">>>")
            res = self.cmds[cmd][0](args)
            print(res)

    def cmd_error_handle(self, cmd):
        return self.cmds[cmd][1]
