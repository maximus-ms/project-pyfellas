from collections import UserDict

from BaseClasses import Topic, Text, CmdProvider


class Note:

    def __init__(self, topic: str, text: str = None, tags: list[str] = None):
        self.topic = Topic(topic)
        self.text = Text(text)
        self.tags = tags

    def __str__(self):
        pass


class Notes(UserDict, CmdProvider):
    cmds_help = (
        ("add-note", "add-note <Topic>", "Add a note to notebook"),
        ("edit-note", "edit-note <Topic>", "Edit note"),
        ("delete-note", "delete-note <Topic>", "Delete a note from notebook"),
        ("show-note", "show-note <Topic>", "Show a note with specified topic"),
        ("find-note", "", ""),
        ("find-note-by-tag", "", "")
    )

    def __init__(self) -> None:
        super().__init__()
        self.cmds = {}
        self.cmds["add-note"] = self.add_note
        self.cmds["show-note"] = self.show_note

    def __str__(self):
        pass

    def help(self):
        return Notes.cmds_help

    def exe(self, cmd, args):
        return self.cmds[cmd](args)

    def add_note(self, args):
        topic, = args
        self.data[topic] = Note(topic)
        return f"Note with topic '{topic}' was added."

    def edit_note(self, note: Note):
        pass

    def delete_note(self, topic: Topic):
        if topic in self.data:
            self.data.pop(topic)

    def show_note(self, args):
        topic, = args
        return self.data[topic]

    def sort_notes(self, notes: list[Note]):
        return sorted(notes, key=lambda note: note.topic.value)

    def find_note_by_topic(self, topic: Topic):
        return self.data[topic] if topic in self.data else None

    def find_note_by_tag(self, note: Note):
        pass
