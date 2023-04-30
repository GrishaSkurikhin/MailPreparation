from os import startfile
from tempfile import NamedTemporaryFile
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt

from Model.Mail import Mail
from Model.Model import Model
from View.ui.textWindow_ui import Ui_textWindow

class FileTextWindow(QtWidgets.QMainWindow):
    def __init__(self, text: str) -> None:
        super().__init__()
        self.resize(400, 300)
        self.setWindowTitle("Текст файла")

        main_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(main_widget)
        layout = QtWidgets.QVBoxLayout(main_widget)

        text_edit = QtWidgets.QTextEdit(main_widget)
        text_edit.setPlainText(text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        main_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

class TextWindow(QtWidgets.QMainWindow):
    def __init__(self, model: Model):
        super(TextWindow, self).__init__()
        self.ui = Ui_textWindow()
        self.ui.setupUi(self)
        self.model = model
        self.listModel = None

        self.ui.listView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.listView.customContextMenuRequested.connect(self.listview_menu_handler)

    def set_data(self, mail: Mail):
        self.set_text(mail)
        self.set_files_list(mail.files)

    def set_text(self, mail:Mail):
        self.ui.textEdit.append(f"{mail.subject}\n")
        self.ui.textEdit.append(f"Время отправки: {mail.date[:-6]}")
        self.ui.textEdit.append(f"Отправитель: {mail.sender['name']} ({mail.sender['name']})")
        recievers = ""
        for reciever in mail.recievers:
            recievers +=  f"{reciever['name']} ({reciever['email']}) [{reciever['type']}], "
        self.ui.textEdit.append("Получатели: " + recievers)
        self.ui.textEdit.append(f"Приоритет: {mail.priority}\n")
        self.ui.textEdit.append("-"*150 + f"\n {mail.body}")
    
    def set_files_list(self, files: list[dict]):
        model = QtGui.QStandardItemModel()
        for file in files:
            item = QtGui.QStandardItem(file["filename"])
            item.setData(file)
            model.appendRow(item)
        model.sort(0)
        self.listModel = model
        self.ui.listView.setModel(model)

    def listview_menu_handler(self, pos):
        indexes = self.ui.listView.selectedIndexes()
        if indexes:
            menu = QtWidgets.QMenu()
            open_action = QtWidgets.QAction("Открыть", self.ui.listView)
            show_text_action = QtWidgets.QAction("Просмотреть", self.ui.listView)
            menu.addAction(open_action)
            menu.addAction(show_text_action)
            action = menu.exec_(self.ui.listView.viewport().mapToGlobal(pos))
            if action == open_action:
                id = self.listModel.itemFromIndex(self.listModel.index(indexes[0].row(), 0)).data()["id"]
                self.open_action(id)
            elif action == show_text_action:
                text = self.listModel.itemFromIndex(self.listModel.index(indexes[0].row(), 0)).data()["text"]
                self.file_text_window = FileTextWindow(text)
                self.file_text_window.show()
    
    def open_action(self, id: str) -> None:
        bytes = self.model.dataStorage.get_file_by_id(id)
        with NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(bytes)
            temp_file.flush()
            startfile(temp_file.name)