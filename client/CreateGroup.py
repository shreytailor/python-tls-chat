# -------------------------------------
# Developed by:
# Shrey Tailor
# -------------------------------------

from protocol import *
from PyQt5.QtWidgets import QDialog, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit


# This class declares the GUI for the dialog through which the client can create a group.
class CreateGroup(QDialog):


    # The constructor arguments are the client socket, and their nickname.
    def __init__(self, socket, nickname):
        super().__init__()
        self.setModal(True)
        self.socket = socket
        self.nickname = nickname
        self.paintScreen()


    def paintScreen(self):
        self.setWindowTitle("Create Group")
        self.move(200, 200)
        self.setFixedSize(400, 100)
        self.show()
        self.createLayout()


    def createLayout(self):
        rootVBox = QVBoxLayout()
        self.setLayout(rootVBox)

        hbox = QHBoxLayout()
        rootVBox.addLayout(hbox)

        nameLabel = QLabel("Group Name", self)
        self.nameTextbox = QLineEdit(self)
        hbox.addWidget(nameLabel)
        hbox.addWidget(self.nameTextbox)

        createButton = QPushButton("Create", self)
        createButton.clicked.connect(self.onCreateGroupClick)
        rootVBox.addWidget(createButton)


    # This is a click listener for the 'Create' button.
    def onCreateGroupClick(self):

        # Check if the input field is not empty.
        if not self.nameTextbox.text() == "":
            try:

                # Attempt to send a message to the server which contains metadata of the group.
                sendData(self.socket, "groups:new", {
                    "groupName": self.nameTextbox.text(),
                    "creator": self.nickname
                })
                self.close()
            except:
                pass
