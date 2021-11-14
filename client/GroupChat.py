# -------------------------------------
# Developed by:
# Shrey Tailor
# -------------------------------------

import time
from PyQt5.QtGui import QFont
from protocol import sendData
from GroupInvite import GroupInvite
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel, QLineEdit, QListWidget, QPushButton, QVBoxLayout


# This class declares the GUI for the group chatting screen.
class GroupChat(QDialog):


    # The constructor parameters are the client socket, group name, and client nickname.
    def __init__(self, socket, groupName, nickname):
        super().__init__()
        self.setModal(True)
        self.socket = socket
        self.nickname = nickname
        self.paintScreen()

        # Send a message to the server that a new user has joined the group.
        sendData(self.socket, "groups:join", {
            "groupName": groupName
        })


    def paintScreen(self):
        self.setWindowTitle(f"Group Chat")
        self.move(200, 200)
        self.setFixedSize(700, 550)
        self.show()
        self.createLayout()


    def createLayout(self):
        rootHBox = QHBoxLayout()
        self.setLayout(rootHBox)

        leftVBox = QVBoxLayout()
        rootHBox.addLayout(leftVBox)

        self.title = QLabel("", self)
        self.title.setFont(QFont("Arial", 14))
        leftVBox.addWidget(self.title)

        self.chatList = QListWidget()
        leftVBox.addWidget(self.chatList)

        textboxButtonHBox = QHBoxLayout()
        self.chatTextbox = QLineEdit(self)
        sendButton = QPushButton("Send", self)
        sendButton.clicked.connect(self.sendMessage)
        textboxButtonHBox.addWidget(self.chatTextbox)
        textboxButtonHBox.addWidget(sendButton)
        leftVBox.addLayout(textboxButtonHBox)

        rightVBox = QVBoxLayout()
        rootHBox.addLayout(rightVBox)

        membersLabel = QLabel("Members", self)
        membersLabel.setFont(QFont("Arial", 14))
        rightVBox.addWidget(membersLabel)

        self.membersList = QListWidget()
        rightVBox.addWidget(self.membersList)

        inviteButton = QPushButton("Invite", self)
        inviteButton.clicked.connect(self.onInviteClick)
        rightVBox.addWidget(inviteButton)


    # This is a close listener for the window.
    def closeEvent(self, event):

        # When the user leaves, it sends a message to the server that they are leaving.
        sendData(self.socket, "groups:leave", {
            "groupName": self.groupInfo["groupName"]
        })
        self.close()


    # This method is used to populate the invitation list in the 'Invite' dialog window.
    def setInviteList(self, inviteList):
        for client in inviteList:
            self.inviteWindow.addClientToList(client)


    # This is a click listener for the 'Invite' button.
    def onInviteClick(self):
        self.inviteWindow = GroupInvite(self.socket, self.groupInfo["groupName"])
        self.inviteWindow.exec_()


    # Whenever the dashboard receives a message for any group related information, i.e. when a new
    # user joins etc, this method is used to repaint the interface.
    def setData(self, payload):
        print(payload)
        self.groupInfo = payload
        self.updateUserList(payload["creator"], payload["clients"])
        self.title.setText(f"{payload['groupName']} by {payload['creator']}")


    # This method is used to repopulate the joined clients list.
    def updateUserList(self, creator, userList):
        self.membersList.clear()

        # Conditional logic for adding user tags such as (Host) and (me).
        for client in userList:
            string = client
            if client == creator:
                string += " (Host)"
            if client == self.nickname:
                string += " (me)"
            self.membersList.addItem(string)


    # This method is used to add a new message to the current list of messages.
    def addMessageToList(self, name, message):

        # Getting the current time in our preferred format.
        t = time.localtime()
        current_time = time.strftime("%H:%M", t)

        if name == self.nickname:
            name = "Me"
        self.chatList.addItem(f"{name} ({current_time}): {message}")


    # This method sends a message to the server regarding a new message in the chat.
    def sendMessage(self):
        if not self.chatTextbox.text() == "":
            sendData(self.socket, "groups:message", {
                "groupName": self.groupInfo["groupName"],
                "message": self.chatTextbox.text(),
                "from": self.nickname
            })
            self.chatTextbox.setText("")