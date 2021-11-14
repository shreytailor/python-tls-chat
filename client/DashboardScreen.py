# -------------------------------------
# Developed by:
# Shrey Tailor
# -------------------------------------

import time
from protocol import *
from PyQt5.QtGui import QFont
from GroupChat import GroupChat
from SingleChat import SingleChat
from CreateGroup import CreateGroup
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel, QListWidget, QMessageBox, QPushButton, QVBoxLayout


# This class declares the GUI for the dashboard, which is opened once the connection has been
# established.
class DashboardScreen(QDialog):


    # The constructor receives a socket and nickname as the parameters.
    def __init__(self, socket, nickname) -> None:
        super().__init__()
        self.setModal(True)
        self.socket = socket
        self.nickname = nickname
        self.paintScreen()

        # Send a message to register its nickname with the server.
        sendData(self.socket, "", {
            "nickname": self.nickname
        })

        # Starting a worker thread which actively listens to the messages coming from the server.
        self.worker = WorkerThread(socket=self.socket)
        self.worker.start()
        self.worker.event_update.connect(self.handleThreadUpdate)


    def paintScreen(self):
        self.setWindowTitle("Chat Dashboard")
        self.move(200, 200)
        self.setFixedSize(400, 500)
        self.show()
        self.createLayout()


    # This method is an event listener for the worker thread, so when the server event is received
    # in the worker thread, it will be passed into this method. Therefore, the conditional behaviour
    # of what happens when a message is received is placed into this method.
    def handleThreadUpdate(self, payload):
        print(payload)

        # Extracting the 'payloadType' and the actual 'payload' from the message.
        payloadType = payload["payloadType"]
        payload = payload["payload"]

        try:
            # Message Reason: updating the client's list of active users and groups.
            if payloadType == "dashboard:update":
                self.updateUserList(payload["users"])
                self.updateGroupList(payload["groups"])

            # Message Reason: someone's has sent you a personal messaging request.
            elif payloadType == "1v1:request":
                promptMessage = f"Do you want to accept a 1v1 request from {payload['initiator']}?"
                prompt = QMessageBox.question(self, "Message", promptMessage, QMessageBox.Yes, QMessageBox.No)

                # Conditionally relay a message to the user whether request is accepted or declined.
                if prompt == QMessageBox.Yes:
                    sendData(self.socket, "1v1:accept", payload)
                    self.chatWindow = SingleChat(self.socket, self.nickname, payload["initiator"])
                    self.chatWindow.exec_()
                else:
                    sendData(self.socket, "1v1:decline", payload)

            # Message Reason: if someone else has accepted your message request.
            elif payloadType == "1v1:accept":
                self.chatWindow.addToMessageList(f"{payload['receiver']} has accepted your request.")

            # Message Reason: if someone else has declined your message request.
            elif payloadType == "1v1:decline":
                self.chatWindow.addToMessageList(f"{payload['receiver']} has declined your request.")
                self.chatWindow.addToMessageList("Feel free to close the window.")

            # Message Reason: someone has sent you a private message.
            elif payloadType == "1v1:message":
                t = time.localtime()
                current_time = time.strftime("%H:%M", t)
                self.chatWindow.addToMessageList(f"{payload['from']} ({current_time}): {payload['message']}")

            # Message Reason: server has sent you information about the group you have joined.
            elif payloadType == "groups:info":
                self.groupChat.setData(payload)

            # Message Reason: there's a new message in the group you are currently in.
            elif payloadType == "groups:message":
                self.groupChat.addMessageToList(payload["from"], payload["message"])

            # Message Reason: the server has sent an 'Invite List' for the group which you are in.
            elif payloadType == "groups:inviteList":
                self.groupChat.setInviteList(payload["clients"])

            # Message Reason: someone has invited you to join a particular group.
            elif payloadType == "groups:invite":
                promptMessage = f"Do you want to accept a request to join the {payload['groupName']} group?"
                prompt = QMessageBox.question(self, "Message", promptMessage, QMessageBox.Yes, QMessageBox.No)

                # If request is accepted, open the group chatting screen, and pass the client socket,
                # the group and client name as the constructor parameters.
                if prompt == QMessageBox.Yes:
                    self.groupChat = GroupChat(self.socket, payload["groupName"], self.nickname)
                    self.groupChat.exec_()
        except:
            pass


    def createLayout(self):
        rootVBox = QVBoxLayout()
        self.setLayout(rootVBox)

        connectedClientsLabel = QLabel("Connected Clients", self)
        connectedClientsLabel.setFont(QFont("Arial", 14))
        rootVBox.addWidget(connectedClientsLabel)

        connectedClientHBox = QHBoxLayout()
        rootVBox.addLayout(connectedClientHBox)

        self.clientList = QListWidget()
        self.clientList.itemClicked.connect(self.onClientSelected)
        connectedClientHBox.addWidget(self.clientList)

        oneOnOneChatButton = QPushButton("1:1 Chat")
        oneOnOneChatButton.clicked.connect(self.onOneOnOneButtonClick)
        connectedClientHBox.addWidget(oneOnOneChatButton)

        chatRoomsLabel = QLabel("Chat rooms (Group chat)", self)
        chatRoomsLabel.setFont(QFont("Arial", 14))
        rootVBox.addWidget(chatRoomsLabel)

        chatRoomsHBox = QHBoxLayout()
        rootVBox.addLayout(chatRoomsHBox)

        self.roomList = QListWidget()
        self.roomList.itemClicked.connect(self.onGroupSelected)
        chatRoomsHBox.addWidget(self.roomList)

        buttonsVBox = QVBoxLayout()
        chatRoomsHBox.addLayout(buttonsVBox)

        createRoomButton = QPushButton("Create", self)
        createRoomButton.clicked.connect(self.onCreateRoomClick)
        buttonsVBox.addStretch()
        buttonsVBox.addWidget(createRoomButton)

        joinRoomButton = QPushButton("Join", self)
        joinRoomButton.clicked.connect(self.onJoinRoomClick)
        buttonsVBox.addWidget(joinRoomButton)
        buttonsVBox.addStretch()


    # This is a click listener for the 'Create' button, which opens an input form.
    def onCreateRoomClick(self):
        window = CreateGroup(self.socket, self.nickname)
        window.exec_()


    # This is a select listener for the active users list.
    def onClientSelected(self, item):
        self.selectedClient = item.text().split(" ")[0]


    # This is a select listener for the active groups list.
    def onGroupSelected(self, item):
        self.selectedGroup = item.text().split(" by ")[0]


    # This is a click listener for the 'Join' button.
    def onJoinRoomClick(self):
        try:

            # If a group is successfully joined, the group chatting dialog is opened.
            self.groupChat = GroupChat(self.socket, self.selectedGroup, self.nickname)
            self.groupChat.exec_()
        except Exception as e:
            pass


    # This is a click listener for the '1v1' button.
    def onOneOnOneButtonClick(self):
        try:
            payload = {
                "initiator": self.nickname,
                "receiver": self.selectedClient 
            }

            # Send a message to the server first, which contains information about who is trying to
            # talk to whom, so it can keep track of this conversation.
            sendData(self.socket, "1v1:request", payload)

            self.chatWindow = SingleChat(self.socket, self.nickname, payload["receiver"])
            self.chatWindow.exec_()
        except Exception as e:
            pass


    # This is the on-close listener for the dashboard window. It relays to the server that you are
    # now leaving the system.
    def closeEvent(self, event):
        sendData(self.socket, "users:leave", {})
        self.close()


    # When the client receives an updated active clients list, this method populates the list view.
    def updateUserList(self, userList):
        self.clientList.clear()
        for user in userList:
            if not user == self.nickname:
                joinTimestamp = int(userList[user].get("joinTimestamp"))
                minutesElapsed = int((int(time.time()) - joinTimestamp) / 60)
                self.clientList.addItem(f"{user} ({minutesElapsed} mins ago)")


    # When the client receives an updated active groups list, this method populates the list view.
    def updateGroupList(self, groupList):
        self.roomList.clear()
        for group in groupList:
            displayName = f"{groupList[group].get('groupName')} by {groupList[group].get('creator')}"
            self.roomList.addItem(displayName)


# This Worker Thread class is used to listen for messages coming from the server, in the background.
# This ensures that the GUI doesn't appear to be frozen to the client.
class WorkerThread(QThread):


    # This is a signalling parameter used to generate events, and execute the callback method.
    event_update = pyqtSignal(dict)


    # A socket is passed in as the constructor parameter so the worker thread can read messages.
    def __init__(self, socket, parent=None):
        super(WorkerThread, self).__init__()
        self.socket = socket


    def run(self):
        while True:
            try:

                # Keep receiving a payload from the socket, and generate an event after doing so.
                payload = receiveData(self.socket)
                self.event_update.emit(payload)
            except:
                pass