import sys
import traceback

from PyQt5.QtWidgets import QApplication
from PyQt5.uic.properties import QtWidgets

from ui import WebRequestApp

def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("error caught!:")
    print("error message:\n", tb)
    QtWidgets.QApplication.quit()

if __name__ == "__main__":
    sys.excepthook = excepthook
    app = QApplication(sys.argv)
    window = WebRequestApp()
    window.show()
    sys.exit(app.exec_())
