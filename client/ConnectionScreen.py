# -------------------------------------
# Developed by:
# Shrey Tailor
# -------------------------------------

import ssl
import socket
from PyQt5 import QtCore
from DashboardScreen import DashboardScreen
from PyQt5.QtWidgets import QLabel, QGridLayout, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton, QWidget


# This class declares the GUI for the splash screen of the application, from which users can join
# the chatting server.
class ConnectionScreen(QWidget):


    def __init__(self) -> None:
        super().__init__()
        self.paintScreen()


    def paintScreen(self):
        self.setWindowTitle("Setup Connection")
        self.move(200, 200)
        self.setFixedSize(400, 180)
        self.show()
        self.createLayout()


    def createLayout(self):
        grid = QGridLayout()
        hbox = QHBoxLayout()

        vbox = QVBoxLayout()
        vbox.addLayout(grid)
        vbox.addLayout(hbox)
        
        ipAddressLabel = QLabel("IP Address", self)
        ipAddressLabel.setAlignment(QtCore.Qt.AlignRight)
        self.ipAddressTextbox = QLineEdit(self)
        self.ipAddressTextbox.setText("localhost")
        grid.addWidget(ipAddressLabel, 0, 0)
        grid.addWidget(self.ipAddressTextbox, 0, 1)

        portLabel = QLabel("Port", self)
        portLabel.setAlignment(QtCore.Qt.AlignRight)
        self.portTextbox = QLineEdit(self)
        self.portTextbox.setText("9988")
        grid.addWidget(portLabel, 1, 0)
        grid.addWidget(self.portTextbox, 1, 1)

        nicknameLabel = QLabel("Nick Name", self)
        nicknameLabel.setAlignment(QtCore.Qt.AlignRight)
        self.nicknameTextbox = QLineEdit(self)
        grid.addWidget(nicknameLabel, 2, 0)
        grid.addWidget(self.nicknameTextbox, 2, 1)

        connectButton = QPushButton("Connect", self)
        connectButton.clicked.connect(self.onConnectClick)
        cancelButton = QPushButton("Cancel", self)
        cancelButton.clicked.connect(self.close)
        hbox.addWidget(connectButton)
        hbox.addWidget(cancelButton)

        self.setLayout(vbox)


    # This is a click listener for the 'Connect' button. It attempts to establish a connection with
    # the chatting server.
    def onConnectClick(self):
        try:
            # Encryption configuration.
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)

            # Creating the socket.
            mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            mySocket = context.wrap_socket(mySocket, server_hostname=self.ipAddressTextbox.text())
            mySocket.connect((self.ipAddressTextbox.text(), int(self.portTextbox.text())))

            # If connection is successful, initiate the Dashboard screen and pass the newly created
            # socket and client's nickname as the constructor parameters.
            dashboard = DashboardScreen(mySocket, self.nicknameTextbox.text())
            dashboard.exec_()
            mySocket.close()
        except:

            # Do nothing if the connection is not successful.
            return