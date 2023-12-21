import re
from collections import UserDict

from BaseClasses import CmdProvider, ErrorWithMsg, Field, get_extra_data_from_user


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


class Tags(Field):

    def validate(self, tags: str) -> [str]:
        if not isinstance(tags, str):
            raise ErrorWithMsg("Tags must be a string.")
        tags_list = tags.strip().replace("#", "").split()
        return tags_list


class Note:

    def __init__(self, topic: Topic, text: Text, tags: Tags):
        self.topic = topic
        self.text = text
        self.text_tags = self.extract_hashtags(text.value)
        self.user_tags = tags.value or []

    @staticmethod
    def extract_hashtags(text: str):
        hashtags = re.findall(r'#\w+', text)
        hashtag_words = [hashtag[1:] for hashtag in hashtags]
        return hashtag_words

    def __str__(self):
        note_text = f"Topic: {self.topic}"
        if self.text and self.text.value:
            note_text += f", text: {self.text}"
        if self.text_tags:
            note_text += f", text tags: {', '.join(self.text_tags)}"
        if self.user_tags:
            note_text += f", user tags: {', '.join(self.user_tags)}"
        return note_text


class Notes(UserDict, CmdProvider):
    ERROR_MESSAGE_NOTE_NOT_FOUND = "Note is not found"
    ERROR_MESSAGE_TAG_NOT_FOUND = "Tag is not found"
    ERROR_EMPTY_NOTES_LIST = "Notes list is empty. Please add some notes first"
    ERROR_MESSAGE_CONTACT_ALREADY_EXISTS = "Contact {} already exists"

    cmds_help = (
        ("add-note", "add-note", "Add a note to notebook"),
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
        self.cmds["find-by-tag"] = self.mixed_search_notes_by_tags
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

    def assert_topic_is_absent(self, topic: str) -> None:
        if topic in self.data:
            raise ErrorWithMsg(Notes.ERROR_MESSAGE_CONTACT_ALREADY_EXISTS.format(topic))
        pass

    def add_note(self, args):
        if len(args) > 0:
            raise ValueError
        list_of_types = [Topic, Text, Tags]
        list_of_prompts = ["Topic: ", "Text: ", "Tags: "]
        data = get_extra_data_from_user(list_of_types, list_of_prompts, self.assert_topic_is_absent)
        topic = data[0].value
        self.data[topic] = Note(data[0], data[1], data[2])
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

    def mixed_search_notes_by_tags(self, search_tags):
        relevant_notes = []
        for note in self.data.values():
            note_tags = note.user_tags + note.text_tags
            relevance = 0
            # Calculate relevance: count of matching tags
            relevance = len(set(search_tags).intersection(note_tags))
            relevance = relevance * 2  # Let full match has more priority
            # Check for partial matching
            for search_tag in search_tags:
                for tag in note_tags:
                    if search_tag.lower() in tag.lower():
                        relevance += 1  # Increase relevance for partial match
            if relevance > 0:
                # Append note and relevance as tuple to relevant_notes list
                relevant_notes.append((note, relevance))
        # Sort notes by relevance (highest to lowest)
        relevant_notes.sort(key=lambda x: x[1], reverse=True)
        # Extract sorted notes without relevance
        sorted_notes = [note[0] for note in relevant_notes]
        return [str(note) for note in sorted_notes]

    def show_all_notes(self, args):
        if len(args) > 0:
            raise ValueError
        return self.get_str_list_of_notes()
