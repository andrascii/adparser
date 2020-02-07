from datetime import datetime
from PySide2 import QtWidgets


def show_message_box(parent, msg):
    message_box = QtWidgets.QMessageBox(parent)
    message_box.setText(msg)
    message_box.exec()


def utc_now():
    return str(datetime.utcnow())

