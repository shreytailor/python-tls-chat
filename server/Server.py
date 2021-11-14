# -------------------------------------
# Developed by:
# Shrey Tailor
# -------------------------------------

import ssl
import time
import socket
import threading
from protocol import *


# Defining the constants required for the server.
port = 9988
hostname = "127.0.0.1"

# Encryption configuration.
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(certfile="cert.pem", keyfile="cert.pem")
context.load_verify_locations("cert.pem")
context.set_ciphers("AES128-SHA")

# Starting up the socket server.
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((hostname, port))
server.listen()
server = context.wrap_socket(server, server_side=True)

print(f"Status - Server starting on {hostname}:{port}.")

# Initializing the data structures required to run the chatting server.
clientData = {}
clientSockets = {}
groups = {}


# This reusable function is used for sending messages at a targetted user by specifying their
# nickname, and message properties such as the payloadType and the actual payload.
def sendToClient(nickname, payloadType, payload):
    socket = findClientSocket(nickname)
    sendData(socket, payloadType, payload)


## This reusable function is used for finding a client's socket, using their nickname as the input.
def findClientSocket(nickname):
    for client in clientSockets:

        # If the key of clientSockets dict is equal to the argument, return the socket object.
        if clientSockets[client].get("nickname") == nickname:
            return client


# This function is used to send a 1v1 chatting request to a client.
def send1v1RequestToClient(request):
    name = request.get("receiver")
    sendToClient(name, "1v1:request", request)


# This reusable function is used for removing a client from this system, using their socket.
def removeClient(clientSocket):
    nickname = clientSockets[clientSocket].get("nickname")
    print(f"Client is leaving: {nickname}")

    # Remove their data from these two dictionaries below.
    clientSockets.pop(clientSocket)
    clientData.pop(nickname)


# This reusable function is used to broadcast a message to all the active connections.
def broadcast(payloadType, payload):
    for client in clientSockets:
        sendData(client, payloadType, payload)


# This reusable function is uused for adding a user to the particular group. The arguments are
# nickname of the user of interest, along with the group they want to join.
def addClientToGroup(groupName, nickname):
    groups[groupName]["clients"].append(nickname)


# This reusable function is used to broadcast a message to all users of a particular group.
def broadcastMessageToGroup(payloadType, payload):
    for client in groups[payload["groupName"]]["clients"]:
        socket = findClientSocket(client)
        sendData(socket, payloadType, payload)


# This function is used when a new client joins the server. It will broadcast the latest list of
# users and groups to all the currently connected clients.
def broadcastDashboardLists():
    broadcast("dashboard:update", {
        "users": clientData,
        "groups": groups
    })


# This function is used to send a list of users, who are "invitable" to a group, to a particular
# user. Users are classified as "invitable" if they are not currently part of the group, and they
# are connected to the server.
def sendGroupInviteList(clientSocket, payload):
    joinedClients = groups[payload["groupName"]]["clients"]
    inviteList = []
    for client in clientData:

        # If clients are not part of the group, add them to the list of the "invitables".
        if client not in joinedClients:
            inviteList.append(client)

    sendData(clientSocket, "groups:inviteList", {
        "clients": inviteList
    })


# This function is used to send an group invite to a currently connected user.
def sendGroupInvite(payload):
    clientSocket = findClientSocket(payload["client"])
    sendData(clientSocket, "groups:invite", {
        "groupName": payload["groupName"]
    })


# This function will run on a new thread for each active user of the chatting server. It consists of
# a while(True) loop which means that the thread will keep listening for messages sent from the client
# , and reply accordingly.
def handle(clientSocket):

    # Extracting client's nickname from the initial payload, and populating the data structures.
    request = receiveData(clientSocket)
    nickname = request["payload"].get("nickname")
    clientSockets[clientSocket] = {
        "nickname": nickname,
    }
    clientData[nickname] = {
        "joinTimestamp": int(time.time())
    }

    # Sending an updated list of clients and servers to all connected clients.
    print(f"Added new client: {nickname}")
    broadcastDashboardLists()

    while True:
        try:
            payload = receiveData(clientSocket)
            payloadType = payload["payloadType"]
            print(payload)
            payload = payload["payload"]

            # Message Reason: this user has left the server.
            if payloadType == "users:leave":
                removeClient(clientSocket)
                broadcastDashboardLists()

            # Message Reason: this user has requested someone to chat with them.
            elif payloadType == "1v1:request":
                send1v1RequestToClient(payload)

            # Message Reason: this user has accepted/declined someone's 1v1 chatting request.
            elif payloadType == "1v1:accept" or payloadType == "1v1:decline":
                sendToClient(payload.get("initiator"), payloadType, payload)

            # Message Reason: this user has just sent someone a personal 1v1 chatting message.
            elif payloadType == "1v1:message":
                sendToClient(payload.get("to"), payloadType, payload)

            # Message Reason: this user has created a new group on the server.
            elif payloadType == "groups:new":
                payload["clients"] = []
                groups[payload["groupName"]] = payload
                broadcastDashboardLists()
            
            # Message Reason: this user has attempted to join a server.
            elif payloadType == "groups:join":
                addClientToGroup(payload["groupName"], nickname)
                broadcastMessageToGroup("groups:info", groups[payload["groupName"]])
                print(groups)

            # Message Reason: this user has left the server they were currently in.
            elif payloadType == "groups:leave":
                groups[payload["groupName"]]["clients"].remove(nickname)
                broadcastMessageToGroup("groups:info", groups[payload["groupName"]])
                print(groups)

            # Message Reason: this user has sent a message in their group.
            elif payloadType == "groups:message":
                broadcastMessageToGroup("groups:message", payload)

            # Message Reason: this user has requested a list of people who can be invited to the group.
            elif payloadType == "groups:inviteList":
                sendGroupInviteList(clientSocket, payload)

            # Message Reason: this user has sent an invitation to someone to join the group.
            elif payloadType == "groups:invite":
                sendGroupInvite(payload)
        except:
            return


# This function accepts new client connections, and starts a new thread for each of them.
def receive():
    while True:
        client, address = server.accept()
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()
receive()