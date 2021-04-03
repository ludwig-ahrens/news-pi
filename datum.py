#!/bin/python3

from datetime import datetime

wochentag = {
    0: "Montag",
    1: "Dienstag",
    2: "Mittwoch",
    3: "Donnestag",
    4: "Freitag",
    5: "Sonnabend",
    6: "Sonntag",
}
monat = {
    1: "Januar",
    2: "Februar",
    3: "März",
    4: "April",
    5: "Mai",
    6: "Juni",
    7: "Juli",
    8: "August",
    9: "September",
    10: "Oktober",
    11: "November",
    12: "Dezember",
}


class Datum:
    def __init__(self, birthday_config, event_config):
        self._birthdays = {
            name: datetime.strptime(val, "%m-%d")
            for name, val in birthday_config.items()
        }
        self._events = event_config

    def birthdays(self):
        today = datetime.now()
        names = [
            name
            for name, dt in self._birthdays.items()
            if dt.month == today.month and dt.day == today.day
        ]
        return names

    def birthday_wishes(self, names):
        wish = lambda x: "Alles Gute zum Geburtstag " + x + "!"
        if len(names) == 0:
            return "WARNING: empty list of birthdays"
        if len(names) == 1:
            return wish(names[0])
        else:
            return wish((" und ").join([(", ").join(names[:-1]), names[-1]]))

    def get_wochentag_datum(self):
        now = datetime.now()
        key = str(now.month) + "-" + str(now.day)
        if key in self._events.keys():
            return wochentag[now.weekday()], self._events[key]
        else:
            today = str(now.day) + ". " + monat[now.month]
            return wochentag[now.weekday()], today


if __name__ == "__main__":
    now = datetime.now()
    print(now.strftime("%Y-%m-%d %H:%M:%S"))
