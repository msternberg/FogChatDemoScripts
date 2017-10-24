import socket
import threading

receiverPort = 3000

if __name__ == '__main__':
    receiverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiverSocket.bind(('', receiverPort))
    receiverSocket.listen(5)
    (androidSocket, address) = receiverSocket.accept()
    print(androidSocket.recv(4096).decode('utf-8'))
