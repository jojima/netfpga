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

total_errors = 0
temp_val = 0

pkts = []
for port in range(2):
    # set parameters
    DA = routerMAC[port]
    SA = "aa:bb:cc:dd:ee:ff"
    TTL = 64
    DST_IP = "192.168.2.1";   #not in the lpm table
    SRC_IP = "192.168.0.1"
    VERSION = 0x4
    nextHopMAC = "dd:55:dd:66:dd:77"

    # Non IP packets
    EtherType = 0x802

    # precreate random packets
    portPkts = []
    for i in range(30):
        portPkts.append(make_IP_pkt(dst_MAC=DA, src_MAC=SA,
                                    EtherType=EtherType, dst_IP=DST_IP,
                                    TTL=TTL, pkt_len=random.randint(60,1514)))
    pkts.append(portPkts)

for port in range(2):
    nftest_regwrite(reg_defines.ROUTER_OP_LUT_NUM_WRONG_DEST_REG(), 0)
    nftest_regwrite(reg_defines.ROUTER_OP_LUT_NUM_NON_IP_RCVD_REG(), 0)
    nftest_regwrite(reg_defines.ROUTER_OP_LUT_NUM_BAD_OPTS_VER_REG(), 0)
    nftest_regwrite(reg_defines.ROUTER_OP_LUT_NUM_BAD_TTLS_REG(), 0)
    nftest_regwrite(reg_defines.ROUTER_OP_LUT_NUM_BAD_CHKSUMS_REG(), 0)
    nftest_regwrite(reg_defines.ROUTER_OP_LUT_NUM_CPU_PKTS_SENT_REG(), 0)

    nftest_barrier()

    # loop for 30 packets
    for i in range(30):
        sent_pkt = pkts[port][i]
        nftest_send_phy('nf2c%d'%port, sent_pkt)
        nftest_expect_dma('nf2c%d'%port, sent_pkt)
    nftest_barrier()

    # Read the counters
    nftest_regread_expect(reg_defines.ROUTER_OP_LUT_NUM_NON_IP_RCVD_REG(), 30)

    nftest_barrier()

nftest_finish()
