import re
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, QTextCodec
from copy import copy
import qdarktheme
from PyQt5.QtCore import QThread, pyqtSignal

from Model.Mail import *
from Model.Model import Model
from View.ui.mainWindow_ui import Ui_MainWindow
from View.textWindow import TextWindow
from View.DBWindow import DBWindow
from View.companiesWindow import CompaniesWindow

class ImportThread(QThread):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    info = pyqtSignal(str)

    def __init__(self, model):
        QThread.__init__(self)
        self.model = model

    def run(self):
        for info, cur_pos in self.model.add_mails():
            self.info.emit(str(info))
            self.progress.emit(round(cur_pos/len(self.model.current_eml.msgs)*100))
        self.finished.emit()

class mainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super(mainWindow, self).__init__()
        self.model = Model()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        QTextCodec.setCodecForLocale(QTextCodec.codecForName("UTF-8"))
        qdarktheme.setup_theme("light")

        # Обработчики
        self.ui.ChooseFileButton.clicked.connect(self.ChooseFileHandler)
        self.ui.FindButton.clicked.connect(self.SearchHandler)
        self.ui.DownloadButton.clicked.connect(self.ImportHandler)
        self.ui.DeleteAllFiltersButton.clicked.connect(self.DeleteAllFiltersHandler)
        self.ui.ExportAllButton.clicked.connect(lambda: self.ExportHandler("all"))
        self.ui.ExportSelectedButton.clicked.connect(lambda: self.ExportHandler("checked"))

        self.ui.MailsTreeView.doubleClicked.connect(self.TreeViewDoubleClickedHandler)
        self.ui.MailsTreeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.MailsTreeView.customContextMenuRequested.connect(self.TreeViewMenuHandler)
        self.ui.DBSettings.triggered.connect(self.DBSettingsHandler)
        self.ui.Companies.triggered.connect(self.CompaniesHandler)

        # Загрузка данных
        users = self.model.dataStorage.get_users()
        companies = self.model.dataStorage.get_companies()
        mails = self.model.dataStorage.get_all_mails()
        self.downloadDataTreeView(mails)
        self.downloadListView(users, "recievers")
        self.downloadListView(users, "senders")
        self.downloadListView(companies, "recieverCompanies")
        self.downloadListView(companies, "sendersCompanies")

    '''
    Загрузка данных
    '''

    def downloadListView(self, users: list[dict], type: str) -> None:
        model = QtGui.QStandardItemModel()
        for user in users:
                if type == "recievers" or type == "senders":
                    item = QtGui.QStandardItem(user["email"] + " - " + user["name"])
                    item.setData(user["email"])
                else: 
                    item = QtGui.QStandardItem(user["name"] + " - " + user["type"])
                    item.setData(user["name"])
                item.setCheckable(True)
                model.appendRow(item)

        model.sort(0)
        if type == "recievers":
            self.modelRecieverslist = model
            self.ui.RecieverListView.setModel(self.modelRecieverslist)
        elif type == "senders":
            self.modelSenderslist = model
            self.ui.SenderListView.setModel(self.modelSenderslist)
        elif type == "recieverCompanies":
            self.modelRecieversCompanieslist = model
            self.ui.RecieverCompaniesListView.setModel(self.modelRecieversCompanieslist)
        elif type == "sendersCompanies":
            self.modelSendersCompanieslist = model
            self.ui.SenderCompaniesListView.setModel(self.modelSendersCompanieslist)

    def downloadDataTreeView(self, mails: list[Mail]):
        self.modelTree = QtGui.QStandardItemModel()
        self.modelTree.setHorizontalHeaderLabels(['Тема', 'Отправитель', 'Получатель', 'Дата'])

        def CreateMailRow(mail: Mail):
            subject_item = QtGui.QStandardItem(mail.subject)
            subject_item.setCheckable(True)
            subject_item.setData(mail)
            sender_item = QtGui.QStandardItem(mail.sender["email"])
            
            recievers_str = ""
            for reciever in mail.recievers:
                if reciever != "":
                    recievers_str += reciever["email"]
            reciever_item = QtGui.QStandardItem(recievers_str)

            datetime_item = QtGui.QStandardItem(mail.date[:-6])
            return [subject_item, sender_item, reciever_item, datetime_item]
        
        for mail in mails:
            row_items = CreateMailRow(mail)
            self.modelTree.appendRow(row_items)
        self.modelTree.sort(3, Qt.DescendingOrder)
        self.ui.MailsTreeView.setModel(self.modelTree)
    
    '''
    Обработчики
    '''

    def TreeViewDoubleClickedHandler(self, index):
        data = self.modelTree.itemFromIndex(self.modelTree.index(index.row(), 0)).data()
        self.text_window = TextWindow(self.model)
        self.text_window.set_data(data)
        self.text_window.show()

    def ChooseFileHandler(self):
        dir_path = QtWidgets.QFileDialog.getExistingDirectory(None, "Выберите директорию")

        if dir_path != "":
            mail_count = self.model.set_current_eml(dir_path)
            self.ui.FileNameLabel.setText("Путь: " + str.split(dir_path, '/')[-1])
            self.ui.MailsCountLabel.setText("Число писем: " + str(mail_count))
            self.ui.InformationBrowser.append(f"По пути {dir_path} найдено {mail_count} писем\n")

    def ImportHandler(self):
        self.import_thread = ImportThread(self.model)
        self.import_thread.info.connect(self.ui.InformationBrowser.append)
        self.import_thread.progress.connect(self.ui.progressBar.setValue)
        self.import_thread.finished.connect(self.import_finished)
        self.import_thread.start()

    def import_finished(self):
        mails = self.model.dataStorage.get_all_mails()
        self.downloadDataTreeView(mails)
        
    def SearchHandler(self):
        def GetCheckedItems(model: QtGui.QStandardItemModel):
            checked_items = []
            for row in range(model.rowCount()):
                index = model.index(row, 0)
                check_state = model.data(index, Qt.CheckStateRole)
                if check_state == Qt.Checked:
                    checked_items.append(model.itemFromIndex(index).data())
            return checked_items
        
        reciviers_list = GetCheckedItems(self.modelRecieverslist)
        senders_list = GetCheckedItems(self.modelSenderslist)
        reciviers_comp_list = GetCheckedItems(self.modelRecieversCompanieslist)
        senders_comp_list = GetCheckedItems(self.modelSendersCompanieslist)

        d_comp_type = {"All": "", "Partners": "partner", "Clients": "client"}
        reciever_comp_type = d_comp_type[self.ui.RecieverCompanyTypeComboBox.currentText()]
        sender_comp_type = d_comp_type[self.ui.SenderCompanyTypeComboBox.currentText()]

        d_priority = {"All": "", "Highest": "1 (Highest)", "High":"2 (High)", "Normal": "3 (Normal)", "Low": "4 (Low)", "Lowest": "5 (Lowest)"}
        priority = d_priority[self.ui.PriorityComboBox.currentText()]

        fromTime = self.ui.FromDateTimeEdit.dateTime().toString('yyyy-MM-dd hh:mm:ss')
        toTime = self.ui.ToDateTimeEdit.dateTime().toString('yyyy-MM-dd hh:mm:ss')
        isTimeSearch = self.ui.IsTimeSearchCheckBox.isChecked()

        keywordsSubject = re.findall(r'\b\w+\b', re.sub(r'[^\w\s]+', '', self.ui.InSubjectEdit.toPlainText()))
        keywordsText = re.findall(r'\b\w+\b', re.sub(r'[^\w\s]+', '', self.ui.InTextEdit.toPlainText()))
        keywordsFiles = re.findall(r'\b\w+\b', re.sub(r'[^\w\s]+', '', self.ui.InFilesEdit.toPlainText()))

        fields = ["reciever_address" for i in range(len(reciviers_list))] + \
                ["sender_address" for i in range(len(senders_list))] + \
                ["reciever_company_name" for i in range(len(reciviers_comp_list))] + \
                ["sender_company_name" for i in range(len(senders_comp_list))]

        filters = reciviers_list + senders_list + reciviers_comp_list + senders_comp_list

        if priority != "":
            fields += ["priority"]
            filters += [priority]

        if reciever_comp_type != "":
            fields += ["reciever_company_type"]
            filters += [reciever_comp_type]

        if sender_comp_type != "":
            fields += ["sender_company_type"]
            filters += [sender_comp_type] 
        
        if self.ui.UnionRadioButton.isChecked():
            logic_operator = "OR"
        elif self.ui.IntersectionRadioButton.isChecked():
            logic_operator = "AND"
        data = self.model.search(fields, filters, fromTime, toTime, isTimeSearch, keywordsSubject, keywordsText, keywordsFiles, logic_operator)
        self.downloadDataTreeView(data)

    def DeleteAllFiltersHandler(self):
        mails = self.model.dataStorage.get_all_mails()
        self.downloadDataTreeView(mails)
    
    def TreeViewMenuHandler(self, pos):
        indexes = self.ui.MailsTreeView.selectedIndexes()
        if indexes:
            menu = QtWidgets.QMenu()
            delete_action = QtWidgets.QAction("Удалить", self.ui.MailsTreeView)
            menu.addAction(delete_action)
            action = menu.exec_(self.ui.MailsTreeView.viewport().mapToGlobal(pos))
            if action == delete_action:
                id = self.modelTree.itemFromIndex(self.modelTree.index(indexes[0].row(), 0)).data().id
                self.model.dataStorage.del_mail(id)
                mails = self.model.dataStorage.get_all_mails()
                self.downloadDataTreeView(mails)
    
    def TraverseTreeview(self, mails, parent_index, type):
        check_state = self.modelTree.data(parent_index, Qt.CheckStateRole)
        if type == "all" or check_state == Qt.Checked:
            mails.append(self.modelTree.itemFromIndex(parent_index).data())
        for row in range(self.modelTree.rowCount(parent_index)):
            child_index = self.modelTree.index(row, 0, parent_index)
            self.TraverseTreeview(mails, child_index)

    def ExportHandler(self, type):
        mails = []
        for row in range(self.modelTree.rowCount()):
            self.TraverseTreeview(mails, self.modelTree.index(row, 0), type)
        format = self.ui.ChooseFormatComboBox.currentText()
        if format == "csv":
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(None, "Сохранить файл", "", "CSV Files (*.csv);;All Files (*)")
            self.model.export_csv(mails, file_path)
            self.ui.InformationBrowser.append("Письма успешно экспортированы в файл: " + file_path)
        elif format == "txt":
            folder_path = QtWidgets.QFileDialog.getExistingDirectory(None, "Выберите папку", ".")
            self.model.export_txt(mails, folder_path)
            self.ui.InformationBrowser.append("Письма успешно экспортированы в папку: " + folder_path)
        elif format == "json":
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(None, "Сохранить файл", "", "JSON Files (*.json);;All Files (*)")
            self.model.export_json(mails, file_path)
            self.ui.InformationBrowser.append("Письма успешно экспортированы в файл: " + file_path)
            
        
    
    def DBSettingsHandler(self):
        self.dbWindow = DBWindow(self.model)
        self.dbWindow.show()

    def CompaniesHandler(self):
        self.companiesWindow = CompaniesWindow(self.model)
        self.companiesWindow.show()
