# -------------------------------------
# Developed by:
# Shrey Tailor
# -------------------------------------

import sys
from SingleChat import SingleChat
from PyQt5.QtWidgets import QApplication
from ConnectionScreen import ConnectionScreen


def startApplication():
    app = QApplication(sys.argv)
    with open("styles/style.qss") as fh:
        app.setStyleSheet(fh.read())
    connectionScreen = ConnectionScreen()
    connectionScreen.show()
    sys.exit(app.exec_())


# This file is used to launch the client GUI.
if __name__ == "__main__":
    startApplication()