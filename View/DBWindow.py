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
        self.model.CreateDB()

    def CheckConnectionHandler(self):
        pass