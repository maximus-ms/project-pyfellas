import re
from collections import UserDict
from datetime import datetime

from BaseClasses import CmdProvider, ErrorWithMsg, Field, get_extra_data_from_user, get_entries_for_next_x_days
from Contacts import Number


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


class Reminder(Field):
    """Class for storing a reminder. Validates the format (expecting DD.MM.YYYY)."""

    def validate(self, reminder: str):
        reminder = reminder.strip()
        try:
            datetime.strptime(reminder, "%d.%m.%Y")
        except:
            raise ErrorWithMsg("Invalid reminder format (DD.MM.YYYY)")
        return reminder


class Note:

    def __init__(self, topic: Topic, text: Text, tags: Tags, reminder: Reminder):
        self.topic = topic
        self.text = text
        self.text_tags = self.extract_hashtags(text.value) if text else []
        self.user_tags = tags.value if tags else []
        self.reminder = reminder

    @staticmethod
    def extract_hashtags(text: str):
        hashtags = re.findall(r'#\w+', text)
        hashtag_words = [hashtag[1:] for hashtag in hashtags]
        return hashtag_words

    def get_reminder_string(self):
        reminder_text = f"Topic: {self.topic}"
        if self.text and self.text.value:
            reminder_text += f", text: {self.text}"
        return reminder_text

    def __str__(self):
        note_text = f"Topic: {self.topic}"
        if self.text and self.text.value:
            note_text += f", text: {self.text}"
        if self.text_tags:
            note_text += f", text tags: {', '.join(self.text_tags)}"
        if self.user_tags:
            note_text += f", user tags: {', '.join(self.user_tags)}"
        if self.reminder:
            note_text += f", reminder: {self.reminder}"
        return note_text


class Notes(UserDict, CmdProvider):
    ERROR_MESSAGE_TAG_NOT_FOUND = "Tag is not found"
    ERROR_EMPTY_NOTES_LIST = "Notes list is empty. Please add some notes first"
    ERROR_MESSAGE_TOPIC_ALREADY_EXISTS = "Topic {} already exists"
    ERROR_MESSAGE_TOPIC_NOT_FOUND = "Topic is not found"
    WELCOME_REMINDERS_NUM_OF_DAYS = 7
    REMINDERS_NUM_OF_DAYS = 7

    cmds_help = (
        ("add-note", "add-note", "Add a note to notebook"),
        ("rename-note", "rename-note", "Rename note topic"),
        ("edit-note", "edit-note", "Edit note text"),
        ("delete-note", "delete-note", "Delete a note from notebook"),
        ("add-tag", "add-tag", "Add one or more tags to note"),
        ("delete-tag", "delete-tag", "Delete one or more tags from note"),
        ("find-note", "find-note", "Find note in notebook by its topic"),
        ("find-by-tag", "find-by-tag <Tag>", "Find note in notebook by its tag"),
        ("all-notes", "all-notes", "Show the complete list of notes"),
        ("reminders", "reminders", "Show reminders for next X days"),
        ("find-note-by-reminder", "find-note-by-reminder", "Find notes appropriate to reminder date"),
    )

    def __init__(self) -> None:
        super().__init__()
        self.__current_topic = None
        self.cmds = {}
        self.cmds["add-note"] = self.add_note
        self.cmds["rename-note"] = self.rename_note
        self.cmds["edit-note"] = self.edit_note
        self.cmds["delete-note"] = self.delete_note
        self.cmds["add-tag"] = self.add_tag
        self.cmds["delete-tag"] = self.delete_tag
        self.cmds["find-note"] = self.find_note_by_topic
        self.cmds["find-note-by-tag"] = self.mixed_search_notes_by_tags
        self.cmds["all-notes"] = self.show_all_notes
        self.cmds["reminders"] = self.reminders
        self.cmds["find-note-by-reminder"] = self.find_note_by_reminder

    def __str__(self):
        return "\n".join(self.get_str_list_of_notes())

    def welcome_message(self):
        notes_reminder = self.__reminders(Notes.WELCOME_REMINDERS_NUM_OF_DAYS)
        num = 0
        for note in notes_reminder:
            if "Topic" in note:
                num += 1
        if num > 0:
            return f"You have {num} reminders(s) during next {Notes.WELCOME_REMINDERS_NUM_OF_DAYS} day(s)"
        else:
            return ""

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
            raise ErrorWithMsg(Notes.ERROR_MESSAGE_TOPIC_ALREADY_EXISTS.format(topic))
        pass

    def assert_topic_exist(self, topic: str) -> None:
        if not topic in self.data:
            raise ErrorWithMsg(Notes.ERROR_MESSAGE_TOPIC_NOT_FOUND.format(topic))
        self.__current_topic = topic

    def assert_tag_exist_and_remove(self, tags: [str]) -> None:
        if self.__current_topic is None:
            raise ErrorWithMsg(Notes.ERROR_MESSAGE_TOPIC_NOT_FOUND)
        note = self.data.get(self.__current_topic)
        for tag in tags:
            if tag in note.text_tags:
                note.text_tags.remove(tag)
            elif tag in note.user_tags:
                note.user_tags.remove(tag)
            else:
                raise ErrorWithMsg(Notes.ERROR_MESSAGE_TAG_NOT_FOUND)

    def add_note(self, args):
        if len(args) > 0:
            raise ValueError
        list_of_types = [Topic, Text, Tags, Reminder]
        list_of_prompts = ["Topic: ", "Text: ", "Tags: ", "Reminder: "]
        data = get_extra_data_from_user(list_of_types, list_of_prompts, self.assert_topic_is_absent)
        topic = data[0].value
        self.data[topic] = Note(data[0], data[1], data[2], data[3])
        return f"Note with topic '{topic}' was added."

    def rename_note(self, args):
        if len(args) > 0:
            raise ValueError
        list_of_types = [Topic, Topic]
        list_of_prompts = ["Old topic: ", "New topic: "]
        list_of_asserts = [self.assert_topic_exist, self.assert_topic_is_absent]
        data = get_extra_data_from_user(list_of_types, list_of_prompts, list_of_asserts, mandatory_all_entries=True)
        old_topic = data[0].value
        new_topic = data[1].value
        note = self.data.pop(old_topic)
        note.topic = new_topic
        self.data[new_topic] = note
        return f"Note with topic '{old_topic}' has been renamed to '{new_topic}'."

    def edit_note(self, args):
        if len(args) > 0:
            raise ValueError
        list_of_types = [Topic, Text]
        list_of_prompts = ["Topic: ", "New text: "]
        list_of_asserts = [self.assert_topic_exist]
        data = get_extra_data_from_user(list_of_types, list_of_prompts, list_of_asserts, mandatory_all_entries=True)
        topic = data[0].value
        new_text = data[1].value
        note = self.data.get(topic)
        note.text.value = new_text
        note.text_tags = Note.extract_hashtags(new_text)
        return f"Text of the note '{topic}' was changed, and text tags were updated."

    def delete_note(self, args):
        if len(args) > 0:
            raise ValueError
        list_of_types = [Topic]
        list_of_prompts = ["Topic: "]
        list_of_asserts = [self.assert_topic_exist]
        data = get_extra_data_from_user(list_of_types, list_of_prompts, list_of_asserts, mandatory_all_entries=True)
        topic = data[0].value
        self.data.pop(topic)
        return f"Note with topic '{topic}' was removed."

    def add_tag(self, args):
        if len(args) > 0:
            raise ValueError
        list_of_types = [Topic, Tags]
        list_of_prompts = ["Topic: ", "Tag(s): "]
        list_of_asserts = [self.assert_topic_exist]
        data = get_extra_data_from_user(list_of_types, list_of_prompts, list_of_asserts, mandatory_all_entries=True)
        topic = data[0].value
        tags = data[1].value
        note = self.data[topic]
        cleaned_tags = [tag.replace("#", "") for tag in tags]
        note.user_tags += cleaned_tags
        return f"Tag(s) {', '.join(cleaned_tags)} added to the note with topic '{topic}'."

    def delete_tag(self, args):
        if len(args) > 0:
            raise ValueError
        list_of_types = [Topic, Tags]
        list_of_prompts = ["Topic: ", "Tag(s): "]
        list_of_asserts = [self.assert_topic_exist, self.assert_tag_exist_and_remove]
        data = get_extra_data_from_user(list_of_types, list_of_prompts, list_of_asserts, mandatory_all_entries=True)
        topic = data[0].value
        tags = data[1].value
        return f"Tag(s) {', '.join(tags)} removed from the note with topic '{topic}'."

    def find_note_by_topic(self, args):
        if len(args) > 0:
            raise ValueError
        list_of_types = [Topic]
        list_of_prompts = ["Topic: "]
        list_of_asserts = [self.assert_topic_exist]
        data = get_extra_data_from_user(list_of_types, list_of_prompts, list_of_asserts, mandatory_all_entries=True)
        topic = data[0].value
        return str(self.data.get(topic))

    def mixed_search_notes_by_tags(self, args):
        if len(args) > 0:
            raise ValueError
        list_of_types = [Tags]
        list_of_prompts = ["Tag(s): "]
        list_of_asserts = []
        data = get_extra_data_from_user(list_of_types, list_of_prompts, list_of_asserts, mandatory_all_entries=True)
        search_tags = data[0].value
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

    def repack_reminders_for_search(self):
        reminders_list = []
        for note in self.data.values():
            if note.reminder:
                entry = {
                    "text": note.get_reminder_string(),
                    "event": datetime.strptime(note.reminder.value, "%d.%m.%Y"),
                }
                reminders_list.append(entry)
        return reminders_list

    def __reminders(self, num_of_days):
        res_reminders_list = []
        if num_of_days > 0:
            reminders_list = self.repack_reminders_for_search()
            res_reminders_list = get_entries_for_next_x_days(reminders_list, num_of_days)
        return res_reminders_list

    def reminders(self, args):
        num_of_days = Notes.REMINDERS_NUM_OF_DAYS
        if len(args) > 0:
            raise ValueError
        list_of_types = [Number]
        list_of_prompts = [f"Days (default {num_of_days}): "]
        data = get_extra_data_from_user(list_of_types, list_of_prompts, mandatory_first_entry=False)
        if not data[0] is None:
            num_of_days = data[0].value
        res_reminders_list = self.__reminders(num_of_days)
        if len(res_reminders_list) == 0:
            return f"No reminders for next {num_of_days} days"
        return res_reminders_list

    def find_note_by_reminder(self, args):
        if len(args) > 0:
            raise ValueError
        relevant_notes = []
        list_of_types = [Reminder]
        list_of_prompts = ["Reminder date: "]
        data = get_extra_data_from_user(list_of_types, list_of_prompts)
        reminder_date = data[0]
        for note in self.data.values():
            if note.reminder == reminder_date:
                relevant_notes.append(str(note))
        if relevant_notes:
            return relevant_notes
        else:
            return "No notes related to this date were found"
