import socket
import threading
import time

IPs = ['128.61.119.89']
PORT = 5000
ipLock = threading.Lock()

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind the socket to port 5000 on this host
serverSocket.bind(('', PORT))
#print(socket.gethostbyname(socket.gethostname()));

#Listen on port 5000
serverSocket.listen(10)

def sendThread(conn):
	#print("Lock Acquire")
	ipLock.acquire()

	for ip in IPs:
		conn.send(ip.encode('utf-8'))
		time.sleep(1)
		#print(ip)

	ipLock.release()
	conn.send("FIN".encode('utf-8'))
	#print("Sent FIN")
	conn.close()

while 1:
	(conn, address) = serverSocket.accept()
	t = threading.Thread(target=sendThread, args=(conn, ))
	t.start()
