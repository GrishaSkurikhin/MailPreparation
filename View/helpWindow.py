from os import startfile
from tempfile import NamedTemporaryFile
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt

class HelpWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.resize(700, 500)
        self.setWindowTitle("Помощь")

        main_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(main_widget)
        layout = QtWidgets.QVBoxLayout(main_widget)

        text_edit = QtWidgets.QTextEdit(main_widget)
        with open('help.html', 'r', encoding="utf-8") as f:
            html_text = f.read()
        text_edit.insertHtml(html_text)
        font = text_edit.font()
        font.setPointSize(12)
        text_edit.setFont(font)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        main_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)