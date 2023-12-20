import re
from collections import UserDict

from BaseClasses import Topic, Text, CmdProvider, ErrorWithMsg


class Note:

    def __init__(self, topic: str, text: str = "", tags: list[str] = None):
        self.topic = Topic(topic)
        self.text = Text(text)
        self.tags = self.extract_hashtags(text)

    def extract_hashtags(self, text: str):
        hashtags = re.findall(r'#\w+', text)
        return hashtags

    def __str__(self):
        text_value = self.text.value if self.text.value is not None else "No text"
        return f"Topic: {self.topic.value}, Text: {text_value}, Tags: {self.tags}"


class Notes(UserDict, CmdProvider):
    cmds_help = (
        ("add-note", "add-note <Topic>", "Add a note to notebook"),
        ("edit-note", "edit-note <Topic>", "Edit note text"),
        ("delete-note", "delete-note <Topic>", "Delete a note from notebook"),
        ("find-note", "find-note <Topic>", "Find note in notebook by its topic"),
        ("find-by-tag", "find-by-tag <Tag>", "Find note in notebook by its tag"),
        ("all-notes", "all-notes", "Show the complete list of notes")
    )

    def __init__(self) -> None:
        super().__init__()
        self.cmds = {}
        self.cmds["add-note"] = self.add_note
        self.cmds["edit-note"] = self.edit_note
        self.cmds["delete-note"] = self.delete_note
        self.cmds["find-note"] = self.find_note_by_topic
        self.cmds["find-by-tag"] = self.find_notes_by_tag
        self.cmds["all-notes"] = self.show_all_notes

    def __str__(self):
        if len(self.data) == 0:
            raise ErrorWithMsg("Please add some notes first")
        return '\n'.join([str(note) for note in self.data.values()])

    def help(self):
        return Notes.cmds_help

    def exe(self, cmd, args):
        return self.cmds[cmd](args)

    def add_note(self, args):
        topic = args[0]
        text = ' '.join(args[1:])
        self.data[topic] = Note(topic, text)
        return f"Note with topic '{topic}' was added."

    def edit_note(self, args):
        topic = args[0]
        new_text = ' '.join(args[1:])
        if topic not in self.data:
            raise ErrorWithMsg("No such note here")
        note = self.data.get(topic)
        note.text.value = new_text
        return f"Text of the note {topic} was changed"

    def delete_note(self, args):
        topic, = args
        if topic not in self.data:
            raise ErrorWithMsg("No such note here")
        self.data.pop(topic)
        return f"Note with topic '{topic}' was removed."

    def find_note_by_topic(self, args):
        topic, = args
        if topic not in self.data:
            raise ErrorWithMsg("Note is not found")
        return str(self.data.get(topic))

    def find_notes_by_tag(self, args):
        search_tags = set(args)
        matching_notes = []
        for note in self.data.values():
            if search_tags.intersection(set(note.tags)):
                matching_notes.append(str(note))
        return '\n'.join(matching_notes)

    def show_all_notes(self, args):
        return str(self)
