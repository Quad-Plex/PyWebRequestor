import sys
from PyQt5.QtWidgets import QApplication
from ui import WebRequestApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WebRequestApp()
    window.show()
    sys.exit(app.exec_())
