#!/bin/env python

from NFTest import *
import random
from RegressRouterLib import *

phy2loop0 = ('../connections/2phy', [])

nftest_init([phy2loop0])
nftest_start()

routerMAC = ["00:ca:fe:00:00:01", "00:ca:fe:00:00:02", "00:ca:fe:00:00:03", "00:ca:fe:00:00:04"]
routerIP = ["192.168.0.40", "192.168.1.40", "192.168.2.40", "192.168.3.40"]

# Clear all tables in a hardware test (not needed in software)
if isHW():
    nftest_invalidate_all_tables()

# Write the mac and IP addresses
for port in range(4):
    nftest_add_dst_ip_filter_entry (port, routerIP[port])
    nftest_set_router_MAC ('nf2c%d'%port, routerMAC[port])

index = 0
subnetIP = "192.168.1.0"
subnetIP2 = "192.168.1.1"
subnetMask = "255.255.255.0"
subnetMask2 = "255.255.255.225"
nextHopIP = "192.168.1.54"
nextHopIP2 = "0.0.0.0"
outPort = 0x1
outPort2 = 0x4
nextHopMAC = "dd:55:dd:66:dd:77"

nftest_add_LPM_table_entry(1, subnetIP, subnetMask, nextHopIP, outPort)
nftest_add_LPM_table_entry(0, subnetIP2, subnetMask2, nextHopIP2, outPort2)
nftest_add_ARP_table_entry(index, nextHopIP, nextHopMAC)
nftest_add_ARP_table_entry(1, subnetIP2, nextHopMAC)

nftest_barrier()

for i in range(100):
    hdr = make_MAC_hdr(src_MAC="aa:bb:cc:dd:ee:ff", dst_MAC=routerMAC[0],
                       EtherType=0x800)/scapy.IP(src="192.168.0.1",
                                                 dst="192.168.1.1", ttl=64)
    exp_hdr = make_MAC_hdr(src_MAC=routerMAC[1], dst_MAC=nextHopMAC,
                           EtherType=0x800)/scapy.IP(src="192.168.0.1",
                                                     dst="192.168.1.1", ttl=63)
    load = generate_load(100)
    pkt = hdr/load
    exp_pkt = exp_hdr/load

    nftest_send_phy('nf2c0', pkt)
    nftest_expect_phy('nf2c1', exp_pkt)

nftest_finish()
