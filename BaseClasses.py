from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime, timedelta, time, date
from calendar import isleap, day_name
from rich.console import Console, Text


class ErrorWithMsg(Exception):
    pass


class Field(ABC):
    """Base class for every field"""

    def __init__(self, value=None):
        self.__value = None
        if not value is None:
            self.value = value

    def __str__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, Field):
            return self.__value == other.value
        if type(other) is str:
            return self.__value == other
        return False

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value):
        self.__value = self.validate(new_value)

    @abstractmethod
    def validate(self, value) -> None:
        """Must raise an exception if not valid or return a value"""
        raise ErrorWithMsg("Unknown value validator")


class CmdProvider(ABC):
    #   __cmds_help_example = (
    #        ("cmd1", "cmd1 <arg>",          "cmd1 is used to call cmd1"),
    #        ("cmd2", "cmd1 <arg1>, <arg2>", "cmd2 is used to call cmd2"),
    #   )

    @abstractmethod
    def exe(self, cmd, args, get_extra_data_from_user_handler):
        raise ErrorWithMsg("Unknown exe()")
        # if cmd == "cmd1":
        # return self.cmd1(args)

    @abstractmethod
    def help(self):
        raise ErrorWithMsg("Unknown help()")
        return []
        # return _Your_class_name_.__cmds_example

    @abstractmethod
    def get_for_file(self):
        raise ErrorWithMsg("Unknown get_for_file()")
        return []

    @abstractmethod
    def set_from_file(self):
        raise ErrorWithMsg("Unknown load_from_file()")
        return []

    def welcome_message(self):
        return None


class FrontBase(ABC):
    @abstractmethod
    def set_cmd_providers(self, items):
        raise ErrorWithMsg("Unknown set_cmd_providers()")

    @abstractmethod
    def set_save_handler(self, handler):
        raise ErrorWithMsg("Unknown set_save_handler()")

    @abstractmethod
    def run(self, handler):
        raise ErrorWithMsg("Unknown run()")

    @abstractmethod
    def get_extra_data_from_user(
        list_of_types,
        list_of_prompts,
        assert_validator=None,
        mandatory_first_entry=True,
        mandatory_all_entries=False,
    ):
        raise ErrorWithMsg("Unknown get_extra_data_from_user()")


def get_entries_for_next_x_days(
    entries,
    x_days=7,
    output_single_line_per_day=False,
    debug=False,
    today=None,
):
    days = defaultdict(list)
    if not today:
        today = datetime.today().date()
    if debug:
        print("Today:", today)
    for entry in entries:
        event = entry["event"].date()
        if not isleap(today.year) and event.month == 2 and event.day == 29:
            if not isleap(event.year):
                # looks like an error
                # it is impossible to have a BD at 29-Feb in non leap year
                # let's just skip this record for now
                continue
            # if User has BD at 29-Feb, usually he/she celebrates at 28-Feb if non-leap year
            event = event.replace(day=28)
        event_this_year = event.replace(year=today.year)
        delta_days = (event_this_year - today).days

        # According to the updated information about this task:
        #   we need entries for the next x_days(7) days, but
        #   if some BDs are on the nearest weekend: shift them forward to Monday
        #   if today is Monday:
        #       take BDs from the past weekend
        #       and BDs on next weekend are out of x_days(7) days and will be celebrated next Monday

        is_monday = today.weekday() == 0
        min_delta = 0
        if is_monday:
            # on Mondays we want to congrats Users from Saturday and Sunday
            min_delta = -2

        if delta_days < min_delta:
            if delta_days < -(366 - x_days):
                event_this_year = event_this_year.replace(year=today.year + 1)
                delta_days = (event_this_year - today).days
            else:
                # there is no reason to handle passed BD if today is not Dec
                # and if BD later than 6-Jan even if today is 31-Dec of leap year
                continue
        elif delta_days >= 363 and is_monday:
            # if today is 1..2-Jan Monday
            event_this_year = event_this_year.replace(year=today.year - 1)
            delta_days = (event_this_year - today).days

        if min_delta <= delta_days < min_delta + x_days:
            remind_at = event_this_year.weekday()
            if remind_at > 4:
                # BD at weekend (days 5 and 6) will congrats at Monday (day 0)
                remind_at = 0
            if debug:
                print(
                    "Event at {}, in {:>2} days ({:>9}), remind at {:>9}".format(
                        entry["event"].date(),
                        delta_days,
                        day_name[event_this_year.weekday()],
                        day_name[remind_at],
                    )
                )
            days[remind_at].append(entry["text"])
    ret_txt = []
    for day_index in range(x_days):
        if x_days <= 7:
            date_text = day_name[day_index]
        else:
            # TODO day_index - it is Monday, Tuesday,... but not days from today. Need to Fix
            date_text = (today + timedelta(days=day_index)).strftime(
                "%d.%m.%Y"
            )
        if len(days[day_index]) > 0:
            if output_single_line_per_day:
                ret_txt.append(
                    "{}: {}".format(
                        date_text, ", ".join(sorted(days[day_index]))
                    )
                )
            else:
                ret_txt.append(date_text)
                for entry in days[day_index]:
                    ret_txt.append(f"  {entry}")
    return ret_txt
