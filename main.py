import sys
from PyQt5.QtWidgets import QApplication

from View.mainWindow import mainWindow

def main():
    app = QApplication(sys.argv)
    view = mainWindow()
    view.show()
    app.exec()
    
if __name__ == "__main__":
    sys.exit(main())