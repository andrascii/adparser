import os
from datetime import datetime, timedelta
from PySide2 import QtWidgets

# timer for updating pages
UPDATE_LOOP_TIMER = 60

# maximum pages to update count
SELECTION_LIMIT = 50

# update page states
STATE_NONE = 0
STATE_TAKEN_FOR_LOADING = 1


def get_days_back_date_string(days_back=0, hours_back=0, minutes_back=0):
    return str(datetime.utcnow() - timedelta(days=days_back, hours=hours_back, minutes=minutes_back))


# removes all non-unique elements in the list
def remove_list_duplicates(lst: list):
    return list(dict.fromkeys(lst))


def remove_if(lst: list, predicate):
    i = 0
    while i < len(lst):
        if predicate(lst[i]):
            lst.remove(lst[i])

        else:
            i += 1


def utc_now_str():
    return str(datetime.utcnow())


# True if specified key found in the passed dictionary and value associated with this key is not None
def has_not_none_key_value(dictionary: dict, key):
    return key in dictionary and dictionary[key] is not None


def all_files_in_folder(path):
    result = []
    for root, directory, file in os.walk(path):
        result += file

    return result


def print_exception_info(module_name: str, exception_info):
    print(module_name + ': ' + str(exception_info))


def show_message_box(parent, msg):
    message_box = QtWidgets.QMessageBox(parent)
    message_box.setText(msg)
    message_box.exec()
