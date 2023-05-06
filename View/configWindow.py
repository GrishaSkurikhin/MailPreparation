from PyQt5 import QtWidgets
from View.ui.configWindow_ui import  Ui_configWindow

class ConfigWindow(QtWidgets.QWidget):
    def __init__(self, DBWindow, model):
        super(ConfigWindow, self).__init__()
        self.ui = Ui_configWindow()
        self.ui.setupUi(self)
        self.model = model
        self.DBWindow = DBWindow

        self.ui.DownloadButton.clicked.connect(self.DownloadConfig)
    
    def DownloadConfig(self):
        data = {}
        data["host"] = self.ui.HostEdit.text()
        data["port"] = self.ui.PortEdit.text()
        data["user"] = self.ui.UserEdit.text()
        data["password"] = self.ui.PasswordEdit.text()
        self.model.config.set_data(data)
        self.ui.OutputLabel.setText("Данные загружены\nв config")
        self.DBWindow.ui.InformationBrowser.append("Данные конфига обновлены")
        try:
            self.model.dataStorage.connect(self.model.config.get_data()["database"])
            self.DBWindow.ui.InformationBrowser.append("Подключение к базе данных установлено")
        except Exception as error:
            self.DBWindow.ui.InformationBrowser.append("Не удалось подключиться к базе данных: " + str(error))