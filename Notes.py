import re
from collections import UserDict

from BaseClasses import CmdProvider, ErrorWithMsg, Field


class Topic(Field):
    """Topic field of Notes"""

    def validate(self, topic: str):
        if not topic:
            raise ErrorWithMsg("Topic cannot be empty.")
        return topic


class Text(Field):
    """Text field of Notes"""

    def validate(self, text: str):
        if not isinstance(text, str):
            raise ErrorWithMsg("Text must be a string.")
        return text


class Note:

    def __init__(self, topic: str, text: str = "", tags: list[str] = None):
        self.topic = Topic(topic)
        self.text = Text(text)
        self.text_tags = self.extract_hashtags(text)
        self.user_tags = tags or []

    @staticmethod
    def extract_hashtags(text: str):
        hashtags = re.findall(r'#\w+', text)
        hashtag_words = [hashtag[1:] for hashtag in hashtags]
        return hashtag_words

    def __str__(self):
        text_value = self.text.value if self.text.value is not None else "No text"
        return f"Topic: {self.topic.value}, Text: {text_value}, Text tags: {self.text_tags}, " \
               f"User tags: {self.user_tags}"


class Notes(UserDict, CmdProvider):
    ERROR_MESSAGE_NOTE_NOT_FOUND = "Note is not found"
    ERROR_MESSAGE_TAG_NOT_FOUND = "Tag is not found"
    ERROR_EMPTY_NOTES_LIST = "Notes list is empty. Please add some notes first"

    cmds_help = (
        ("add-note", "add-note <Topic>", "Add a note to notebook"),
        ("rename-note", "rename-note <Topic> <New Topic>", "Rename note topic"),
        ("edit-note", "edit-note <Topic> <Text>", "Edit note text"),
        ("delete-note", "delete-note <Topic>", "Delete a note from notebook"),
        ("add-tag", "add-tag <Topic> <Tag(s)>", "Add one or more tags to note"),
        ("delete-tag", "delete-tag <Topic> <Tag(s)>", "Delete one or more tags from note"),
        ("find-note", "find-note <Topic>", "Find note in notebook by its topic"),
        ("find-by-tag", "find-by-tag <Tag>", "Find note in notebook by its tag"),
        ("all-notes", "all-notes", "Show the complete list of notes"),
    )

    def __init__(self) -> None:
        super().__init__()
        self.cmds = {}
        self.cmds["add-note"] = self.add_note
        self.cmds["rename-note"] = self.rename_note
        self.cmds["edit-note"] = self.edit_note
        self.cmds["delete-note"] = self.delete_note
        self.cmds["add-tag"] = self.add_tag
        self.cmds["delete-tag"] = self.delete_tag
        self.cmds["find-note"] = self.find_note_by_topic
        self.cmds["find-by-tag"] = self.find_notes_by_tag
        self.cmds["all-notes"] = self.show_all_notes

    def __str__(self):
        return "\n".join(self.get_str_list_of_notes())

    def get_str_list_of_notes(self):
        if len(self.data) == 0:
            raise ErrorWithMsg(Notes.ERROR_EMPTY_NOTES_LIST)
        return [str(note) for note in self.data.values()]

    def help(self):
        return Notes.cmds_help

    def exe(self, cmd, args):
        return self.cmds[cmd](args)

    def add_note(self, args):
        if len(args) < 1:
            raise ValueError
        topic = args[0]
        text = ' '.join(args[1:])
        self.data[topic] = Note(topic, text)
        return f"Note with topic '{topic}' was added."

    def rename_note(self, args):
        old_topic, new_topic = args
        if old_topic not in self.data:
            raise ErrorWithMsg(Notes.ERROR_MESSAGE_NOTE_NOT_FOUND)
        note = self.data.pop(old_topic)
        self.data[new_topic] = Note(new_topic, note.text.value, note.user_tags)
        return f"Note with topic '{old_topic}' has been renamed to '{new_topic}'."

    def edit_note(self, args):
        if len(args) < 1:
            raise ValueError
        topic = args[0]
        new_text = ' '.join(args[1:])
        if topic not in self.data:
            raise ErrorWithMsg(Notes.ERROR_MESSAGE_NOTE_NOT_FOUND)
        note = self.data.get(topic)
        note.text.value = new_text
        note.text_tags = Note.extract_hashtags(new_text)
        return f"Text of the note {topic} was changed, and text tags were updated."

    def delete_note(self, args):
        topic, = args
        if topic not in self.data:
            raise ErrorWithMsg(Notes.ERROR_MESSAGE_NOTE_NOT_FOUND)
        self.data.pop(topic)
        return f"Note with topic '{topic}' was removed."

    def add_tag(self, args):
        topic, *tags = args
        if topic not in self.data:
            raise ErrorWithMsg(Notes.ERROR_MESSAGE_NOTE_NOT_FOUND)
        note = self.data[topic]
        cleaned_tags = [tag[1:] if tag.startswith('#') else tag for tag in tags]
        note.user_tags.extend(cleaned_tags)
        return f"Tag(s) {', '.join(cleaned_tags)} added to the note with topic '{topic}'."

    def delete_tag(self, args):
        topic, *tags = args
        if topic not in self.data:
            raise ErrorWithMsg(Notes.ERROR_MESSAGE_NOTE_NOT_FOUND)
        note = self.data[topic]
        for tag in tags:
            if tag in note.text_tags:
                note.text_tags.remove(tag)
            elif note.user_tags and tag in note.user_tags:
                note.user_tags.remove(tag)
            else:
                raise ErrorWithMsg(Notes.ERROR_MESSAGE_TAG_NOT_FOUND)
        return f"Tag(s) {', '.join(tags)} removed from the note with topic '{topic}'."

    def find_note_by_topic(self, args):
        topic, = args
        if topic not in self.data:
            raise ErrorWithMsg(Notes.ERROR_MESSAGE_NOTE_NOT_FOUND)
        return str(self.data.get(topic))

    def sort_notes_by_tags(self, notes_dict):
        return notes_dict.values()

    def find_notes_by_tag(self, args):
        # TODO concatenate tags and sort and break if first found and save tag of matched note
        # {"tag": "note"} --> list(notes)
        notes_dict = {}
        search_tags = set(args)
        matching_notes = []
        for note in self.data.values():
            if search_tags.intersection(set(note.tags)):
                matching_notes.append(str(note))
        return self.sort_notes_by_tags(notes_dict)

    def show_all_notes(self, args):
        if len(args) > 0:
            raise ValueError
        return self.get_str_list_of_notes()
