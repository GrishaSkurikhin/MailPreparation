from PyQt5 import QtWidgets
from View.ui.DBWindow_ui import Ui_DBWindow
from View.configWindow import ConfigWindow

class DBWindow(QtWidgets.QWidget):
    def __init__(self, model):
        super(DBWindow, self).__init__()
        self.ui = Ui_DBWindow()
        self.ui.setupUi(self)
        self.model = model

        self.ui.CreateDB.clicked.connect(self.CreateDBHandler)
        self.ui.CheckConnection.clicked.connect(self.CheckConnectionHandler)
        self.ui.ConnectionSettings.clicked.connect(self.ConnectionSettingsHandler)
    
    def ConnectionSettingsHandler(self):
        self.companiesWindow = ConfigWindow(self, self.model)
        self.companiesWindow.show()

    def CreateDBHandler(self):
        try:
            self.model.create_db()
            self.ui.InformationBrowser.append("База данных успешно создана")
            try:
                self.model.dataStorage.connect(self.model.config.get_data()["database"])
                self.ui.InformationBrowser.append("Подключение к базе данных установлено")
            except Exception as error:
                self.ui.InformationBrowser.append("Не удалось подключиться к базе данных: " + str(error))
        except Exception as error:
            self.ui.InformationBrowser.append("База данных не создана: " + str(error))

    def CheckConnectionHandler(self):
        try:
            if self.model.dataStorage.connection is not None:
                self.ui.InformationBrowser.append("Подключение установлено")
            else:
                self.ui.InformationBrowser.append("Подключение не установлено")
        except:
            self.ui.InformationBrowser.append("Подключение не установлено")