from scapy.all import *
import ipaddress
arp_req_filter = 'arp'
ips=unicode("192.168.42.129/32", "utf-8")  ## Update this with IP of Android phone
mac = "b8:27:eb:c7:eb:59"  ## Update w/ MAC of interface facing Fog LAN
def sendReply (dstmac, reqip, dstip):
    print 'Need to send reply to %s : w/ MAC Addr of %s' % (dstmac, reqip)
    pkt = send (ARP(op=2, hwsrc=mac, psrc=reqip, hwdst=dstmac, pdst=dstip), iface="eth0")
def respond (arp):
    dstip = unicode(arp.fields ['pdst'], "utf-8")
    srcip = unicode(arp.fields ['psrc'], "utf-8")
    srcmac = arp.fields ['hwsrc']
    print 'Recv ARP Req from %s %s for IP %s' % (srcmac, srcip, dstip)
    if ipaddress.ip_address (dstip) in ipaddress.ip_network(ips):
        sendReply (srcmac, dstip, srcip)
while True:
    pkts = sniff (filter=arp_req_filter, count=1, iface="eth0")
    if len (pkts) == 0:
        continue
    pkt = pkts[0]
    if ARP in pkt and pkt[ARP].op == 1:	# ARP Request
        respond (pkt[ARP])
