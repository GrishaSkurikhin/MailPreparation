import sys
from PyQt5.QtWidgets import QApplication

from View.mainWindow import MainWindow

def main():
    app = QApplication(sys.argv)
    view = MainWindow()
    view.show()

    app.aboutToQuit.connect(lambda: view.model.dataStorage.close())
    return app.exec()
    
if __name__ == "__main__":
    sys.exit(main())