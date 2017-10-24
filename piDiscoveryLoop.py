import socket
import time
import threading

class RaspberryPi:

    discoveryIP = 'localhost'
    broadcastAddress = '255.255.255.255'
    discoveryPort = 5000
    broadcastPort = 12345
    mobilePort = 4000
    broadcastRespond = "DISCOVERY ACK"
    mobileRequest = "ANDROID REQ"
    globalIPs = []

    def createDisoverySocket(self, timeout):
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.settimeout(timeout)
        clientSocket.connect((self.discoveryIP, self.discoveryPort))
        return clientSocket

    def handleSocketError(self, clientSock, msg):
        try:
            if clientSock != None:
                clientSock.close()
        except socket.error as msg:
            pass
        print(msg)
        print("Saved IP List is: " + str(self.globalIPs))
        time.sleep(5)

    # Uses a discovery protocol to find the IP address of the nearest discovery server.
    # Sends out a broadcast and waits for a response from a nearby discovery server
    def findDiscoveryIP(self):
        udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpSocket.bind(('', self.broadcastPort)) #bind the pi discovery socket to port 12345
        udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        data = ""
        serverAddr = ""
        while data != self.broadcastRespond and serverAddr == "":
            udpSocket.sendto("PI CONNECTION".encode('utf-8'), (self.broadcastAddress, self.broadcastPort)) #send a discovery broadcast Request
            data, serverAddr = udpSocket.recvfrom(4096)
        return serverAddr

    def sendToAndroid(self):
        req = ""

        #set up a tcp server for the android device to connect to
        tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpSocket.bind(('', self.mobilePort))
        tcpSocket.listen(5)

        #when the android device sets up a tcp connection, send the first IP in globalIPs,
        # or an empty string if there are no globalIPs available
        print(tcpSocket)
        while True:
            print("Waiting for android to connect")
            (mobileSocket, mobileAddress) = tcpSocket.accept()
            print("Accepted android connection")
            req = mobileSocket.recv(4096).decode('utf-8')
            print("REQ IS: " +  req)
            print("globalIPs IS: " + str(self.globalIPs))
            if (req == self.mobileRequest):
                print("CORRECT REQUEST")
                if len(self.globalIPs) > 0:
                    ip = self.globalIPs[0] + "\n";
                    mobileSocket.send(ip.encode('utf-8'))
                    print("SENT: " + ip)
                else:
                    mobileSocket.send("".encode('utf-8'))

    #This should update the IP list from the discovery server every 5 seconds
    #If it cannot connect, wait another 5 seconds
    def updateIpList(self):
        while True:
            try:
                data = ""
                IPs = []

                try:
                    # connect the socket to the server
                    clientSocket = self.createDisoverySocket(2)
                except socket.error as msg:
                    self.handleSocketError(None, msg)
                    continue

                #print("Updating Fog IPs")
                while data != "FIN":
                        data = clientSocket.recv(1024).decode('utf-8')
                        IPs.append(data)
                clientSocket.close()
                self.globalIPs = IPs[:-1]
                print("Current IP List is: " + str(self.globalIPs))
                time.sleep(5)

            #If something is wrong with the server, keep the global IPs the way it is
            # and retry the update in 5 seconds
            except socket.timeout as timeout:
                self.handleSocketError(clientSocket, timeout)
                continue
            except socket.error as error:
                self.handleSocketError(None, error)

if __name__=='__main__':
    #discoverIP = findDiscoveryIP()
    rPI = RaspberryPi()
    print("IP is " + socket.gethostbyname(socket.gethostname()))
    updateIpThread = threading.Thread(target=rPI.updateIpList)
    androidThread = threading.Thread(target=rPI.sendToAndroid)
    updateIpThread.start()
    androidThread.start()
