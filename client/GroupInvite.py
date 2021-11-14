# -------------------------------------
# Developed by:
# Shrey Tailor
# -------------------------------------

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog, QLabel, QListWidget, QPushButton, QVBoxLayout
from protocol import sendData


# This class declares the GUI for the group invitation screen.
class GroupInvite(QDialog):


    # The constuctor parameters are the client socket and the group name.
    def __init__(self, socket, groupName):
        super().__init__()
        self.setModal(True)
        self.socket = socket
        self.groupName = groupName
        self.paintScreen()

        # Client requests server for the 'invitation list'.
        sendData(self.socket, "groups:inviteList", {
            "groupName": self.groupName
        })


    def paintScreen(self):
        self.setWindowTitle("Invite Friends")
        self.setFixedSize(250, 500)
        self.show()
        self.createLayout()


    def createLayout(self):
        rootVBox = QVBoxLayout()
        self.setLayout(rootVBox)

        inviteTitle = QLabel("Invite Clients", self)
        inviteTitle.setFont(QFont("Arial", 14))
        rootVBox.addWidget(inviteTitle)

        self.clientList = QListWidget()
        self.clientList.itemClicked.connect(self.onClientSelected)
        rootVBox.addWidget(self.clientList)

        inviteButton = QPushButton("Invite", self)
        inviteButton.clicked.connect(self.onInviteClick)
        rootVBox.addWidget(inviteButton)


    # This method is used to populate the client list.
    def addClientToList(self, client):
        self.clientList.addItem(client)


    # This is a select listener for the client list.
    def onClientSelected(self, client):
        self.selectedClient = client.text()


    # This is the click listener for the 'Invite' button.
    def onInviteClick(self):
        try:

            # Send a message to the server about the client invitation.
            sendData(self.socket, "groups:invite", {
                "groupName": self.groupName,
                "client": self.selectedClient
            })
            self.close()
        except Exception as e:
            pass