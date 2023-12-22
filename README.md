# GoITNeo Python project-pyfellas

## Bot-assistant
This is a personal CLI-based assistant which helps to keep a contact-book and note-book always with you.
### Basic functionality
##### 1. Address book
Basic features
 - save name, phone number, e-mail, birthday, address of a person
 - validate an input data depending on the data type (e-mail, date, phone, etc)
 - search record(s) by any field (name, phone, etc)
 - add/edit/delete any field of a record
 - show a list of birthdays for next X days

##### 2. Note book
Basic features
 - save topic, text of a note
 - search record(s) by topic
 - edit topic or/and text of a record

Extra features
 - user's tags
 - text embedded tags (eg "This is an embedded #tag in the text.")
 - search record(s) by tag(s), result is sorted by relevance
 - reminder
 - search record(s) by reminder
 - show a list of notes with reminders for next X days

##### 3. Assistant
Basic features
 - store data to a disc

Extra features
 - prompts for user's command
 - colorful
 - long output is printed in chunks
 - installable
 - show message if there are birthdays or/and reminders during next X days
 - show quote of the day
 - configuration parameters:
    * User name for welcome message
    * Show birthday message
    * Show reminder message
    * Show quote
    * Set color theme
    * Enable prompts for command
```
~$ assistant
Hi, this is your assistant
  You have 2 birthday(s) during next 7 day(s)
  You have 1 reminders(s) during next 7 day(s)
  Quote for today: "Freeing oneself from words is liberation." - Bodhidharma (https://zenquotes.io/)
write your command ('h|help' for details)
>>> settings
Name /'~' to delete/ (current John) : Joe
Show birthdays (current True):
Show reminders (current True):
Show quote (current True):
Color theme (current 1):
Use prompt (current True):
New settings applied
>>>
```


##
### How to make a setup package:

``` python ./make_package.py```

### How to install
``` pip install ./assistant```

### How to use
```~$ assistant```

#
#
#
Enjoy. And let the power be with you
