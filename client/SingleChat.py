# -------------------------------------
# Developed by:
# Shrey Tailor
# -------------------------------------

import time
from protocol import *
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel, QLineEdit, QListWidget, QPushButton, QVBoxLayout


# This class declares the GUI for the 1v1 personal chatting screen.
class SingleChat(QDialog):


    # The constructor parameters are the current client socket, their nickname, and nickname of the
    # person whom they are talking with.
    def __init__(self, socket, me, otherClient) -> None:
        super().__init__()
        self.setModal(True)
        self.socket = socket
        self.me = me
        self.otherClient = otherClient
        self.paintScreen()


    def paintScreen(self):
        self.setWindowTitle(f"Chat with {self.otherClient}")
        self.move(200, 200)
        self.setFixedSize(350, 450)
        self.createLayout()
    
    
    def createLayout(self):
        rootVBox = QVBoxLayout()
        hbox = QHBoxLayout()

        title = QLabel(f"Chat with {self.otherClient}", self)
        title.setFont(QFont("Arial", 14))
        rootVBox.addWidget(title)

        self.messageList = QListWidget()
        rootVBox.addWidget(self.messageList)

        self.messageTextbox = QLineEdit(self)
        hbox.addWidget(self.messageTextbox)

        sendButton = QPushButton("Send", self)
        sendButton.clicked.connect(self.sendMessage)
        hbox.addWidget(sendButton)

        rootVBox.addLayout(hbox)

        self.setLayout(rootVBox)
        self.show()


    # This method is used to add a message to the list of messages.
    def addToMessageList(self, string):
        self.messageList.addItem(string)


    # This method is used to send a message payload to the server.
    def sendMessage(self):

        # Check initially that the input field is not empty.
        if not self.messageTextbox.text() == "":
            
            # Send a payload which contains the source client, destination client, and the message
            # which is supposed to be delivered.
            payload = {
                "from": self.me,
                "to": self.otherClient,
                "message": self.messageTextbox.text()
            }
            sendData(self.socket, "1v1:message", payload)

            # Add the message being sent to your list of messages.
            t = time.localtime()
            current_time = time.strftime("%H:%M", t)
            self.addToMessageList(f"Me ({current_time}): {self.messageTextbox.text()}")
            self.messageTextbox.setText("")