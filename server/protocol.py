# -------------------------------------
# Developed by:
# Shrey Tailor
# -------------------------------------

import pickle

# This value is assumed to be the maximum message size within this chatting application.
MESSAGE_SIZE = 4096

# This reusable function is used for sending messages to with to a particular socket. The message
# details (such as 'payloadType' and the 'payload' itself) are passed in as the arguments.
def sendData(socket, payloadType, payload):

    # This dictionary defines the format of the message.
    dictionary = {
        "payloadType": payloadType,
        "payload": payload
    }

    # Pickling and sending the message.
    socket.send(pickle.dumps(dictionary))

# This reusable function is used for receiving the messages on the other side.
def receiveData(socket):
    message = pickle.loads(socket.recv(MESSAGE_SIZE))
    return message