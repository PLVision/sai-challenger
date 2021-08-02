import socket
import pytest
from sai import SaiObjType
from ptf.testutils import simple_tcp_packet, send_packet, verify_packets, verify_packet, verify_no_packet_any, verify_no_packet, verify_any_packet_any_port


def test_l2_access_to_access_vlan(npu, dataplane):
    vlan_id = "10"
    macs = ['00:11:11:11:11:11', '00:22:22:22:22:22']
    max_port = 2
    vlan_mbr_oids = []

    vlan_oid = npu.create(SaiObjType.VLAN, ["SAI_VLAN_ATTR_VLAN_ID", vlan_id])

    for idx in range(max_port):
        npu.remove_vlan_member(npu.default_vlan_oid, npu.dot1q_bp_oids[idx])
        vlan_mbr = npu.create_vlan_member(vlan_oid, npu.dot1q_bp_oids[idx], "SAI_VLAN_TAGGING_MODE_UNTAGGED")
        vlan_mbr_oids.append(vlan_mbr)
        npu.set(npu.port_oids[idx], ["SAI_PORT_ATTR_PORT_VLAN_ID", vlan_id])
        npu.create_fdb(vlan_oid, macs[idx], npu.dot1q_bp_oids[idx])

    try:
        if npu.run_traffic:
            pkt = simple_tcp_packet(eth_dst=macs[1],
                                    eth_src=macs[0],
                                    ip_dst='10.0.0.1',
                                    ip_id=101,
                                    ip_ttl=64)

            send_packet(dataplane, 0, pkt)
            verify_packets(dataplane, pkt, [1])
    finally:
        for idx in range(max_port):
            npu.remove_fdb(vlan_oid, macs[idx])
            npu.remove(vlan_mbr_oids[idx])
            npu.create_vlan_member(npu.default_vlan_oid, npu.dot1q_bp_oids[idx], "SAI_VLAN_TAGGING_MODE_UNTAGGED")
            npu.set(npu.port_oids[idx], ["SAI_PORT_ATTR_PORT_VLAN_ID", npu.default_vlan_id])

        npu.remove(vlan_oid)


def test_l2_trunk_to_trunk_vlan(npu, dataplane):
    vlan_id = "10"
    macs = ['00:11:11:11:11:11', '00:22:22:22:22:22']

    vlan_oid = npu.create(SaiObjType.VLAN, ["SAI_VLAN_ATTR_VLAN_ID", vlan_id])
    vlan_member1 = npu.create_vlan_member(vlan_oid, npu.dot1q_bp_oids[0], "SAI_VLAN_TAGGING_MODE_TAGGED")
    vlan_member2 = npu.create_vlan_member(vlan_oid, npu.dot1q_bp_oids[1], "SAI_VLAN_TAGGING_MODE_TAGGED")
    npu.create_fdb(vlan_oid, macs[0], npu.dot1q_bp_oids[0])
    npu.create_fdb(vlan_oid, macs[1], npu.dot1q_bp_oids[1])

    try:
        if npu.run_traffic:
            pkt = simple_tcp_packet(eth_dst=macs[1],
                                    eth_src=macs[0],
                                    dl_vlan_enable=True,
                                    vlan_vid=10,
                                    ip_dst='10.0.0.1',
                                    ip_id=101,
                                    ip_ttl=64)

            send_packet(dataplane, 0, pkt)
            verify_packets(dataplane, pkt, [1])
    finally:
        npu.flush_fdb_entries(["SAI_FDB_FLUSH_ATTR_BV_ID", vlan_oid])
        npu.remove(vlan_member1)
        npu.remove(vlan_member2)
        npu.remove(vlan_oid)


def test_l2_access_to_trunk_vlan(npu, dataplane):
    vlan_id = "10"
    macs = ['00:11:11:11:11:11', '00:22:22:22:22:22']

    vlan_oid = npu.create(SaiObjType.VLAN, ["SAI_VLAN_ATTR_VLAN_ID", vlan_id])

    npu.remove_vlan_member(npu.default_vlan_oid, npu.dot1q_bp_oids[0])
    npu.create_vlan_member(vlan_oid, npu.dot1q_bp_oids[0], "SAI_VLAN_TAGGING_MODE_UNTAGGED")
    npu.create_vlan_member(vlan_oid, npu.dot1q_bp_oids[1], "SAI_VLAN_TAGGING_MODE_TAGGED")
    npu.set(npu.port_oids[0], ["SAI_PORT_ATTR_PORT_VLAN_ID", vlan_id])

    for idx in range(2):
        npu.create_fdb(vlan_oid, macs[idx], npu.dot1q_bp_oids[idx])

    try:
        if npu.run_traffic:
            pkt = simple_tcp_packet(eth_dst=macs[1],
                                    eth_src=macs[0],
                                    ip_dst='10.0.0.1',
                                    ip_id=102,
                                    ip_ttl=64)
            exp_pkt = simple_tcp_packet(eth_dst=macs[1],
                                    eth_src=macs[0],
                                    ip_dst='10.0.0.1',
                                    dl_vlan_enable=True,
                                    vlan_vid=10,
                                    ip_id=102,
                                    ip_ttl=64,
                                    pktlen=104)
            send_packet(dataplane, 0, pkt)
            verify_packets(dataplane, exp_pkt, [1])
    finally:
        for idx in range(2):
            npu.remove_fdb(vlan_oid, macs[idx])
            npu.remove_vlan_member(vlan_oid, npu.dot1q_bp_oids[idx])
        npu.create_vlan_member(npu.default_vlan_oid, npu.dot1q_bp_oids[0], "SAI_VLAN_TAGGING_MODE_UNTAGGED")
        npu.set(npu.port_oids[0], ["SAI_PORT_ATTR_PORT_VLAN_ID", npu.default_vlan_id])
        npu.remove(vlan_oid)


def test_l2_trunk_to_access_vlan(npu, dataplane):
    vlan_id = "10"
    macs = ['00:11:11:11:11:11', '00:22:22:22:22:22']

    vlan_oid = npu.create(SaiObjType.VLAN, ["SAI_VLAN_ATTR_VLAN_ID", vlan_id])
    npu.create_vlan_member(vlan_oid, npu.dot1q_bp_oids[0], "SAI_VLAN_TAGGING_MODE_TAGGED")
    npu.remove_vlan_member(npu.default_vlan_oid, npu.dot1q_bp_oids[1])
    npu.create_vlan_member(vlan_oid, npu.dot1q_bp_oids[1], "SAI_VLAN_TAGGING_MODE_UNTAGGED")
    npu.set(npu.port_oids[1], ["SAI_PORT_ATTR_PORT_VLAN_ID", vlan_id])

    for idx in range(2):
        npu.create_fdb(vlan_oid, macs[idx], npu.dot1q_bp_oids[idx])

    try:
        if npu.run_traffic:
            pkt = simple_tcp_packet(eth_dst=macs[1],
                                    eth_src=macs[0],
                                    ip_dst='10.0.0.1',
                                    dl_vlan_enable=True,
                                    vlan_vid=10,
                                    ip_id=102,
                                    ip_ttl=64,
                                    pktlen=104)
            exp_pkt = simple_tcp_packet(eth_dst=macs[1],
                                    eth_src=macs[0],
                                    ip_dst='10.0.0.1',
                                    ip_id=102,
                                    ip_ttl=64)
            send_packet(dataplane, 0, pkt)
            verify_packets(dataplane, exp_pkt, [1])
    finally:
        for idx in range(2):
            npu.remove_fdb(vlan_oid, macs[idx])
            npu.remove_vlan_member(vlan_oid, npu.dot1q_bp_oids[idx])
        npu.create_vlan_member(npu.default_vlan_oid, npu.dot1q_bp_oids[1], "SAI_VLAN_TAGGING_MODE_UNTAGGED")
        npu.set(npu.port_oids[1], ["SAI_PORT_ATTR_PORT_VLAN_ID", npu.default_vlan_id])
        npu.remove(vlan_oid)


def test_l2_flood(npu, dataplane):
    vlan_id = "10"
    macs = ['00:11:11:11:11:11', '00:22:22:22:22:22']
    vlan_mbr_oids = []

    vlan_oid = npu.create(SaiObjType.VLAN, ["SAI_VLAN_ATTR_VLAN_ID", vlan_id])

    for idx in range(3):
        npu.remove_vlan_member(npu.default_vlan_oid, npu.dot1q_bp_oids[idx])
        vlan_mbr = npu.create_vlan_member(vlan_oid, npu.dot1q_bp_oids[idx], "SAI_VLAN_TAGGING_MODE_UNTAGGED")
        vlan_mbr_oids.append(vlan_mbr)
        npu.set(npu.port_oids[idx], ["SAI_PORT_ATTR_PORT_VLAN_ID", vlan_id])

    try:
        if npu.run_traffic:
            pkt = simple_tcp_packet(eth_dst=macs[1],
                                    eth_src=macs[0],
                                    ip_dst='10.0.0.1',
                                    ip_id=107,
                                    ip_ttl=64)

            send_packet(dataplane, 0, pkt)
            verify_packets(dataplane, pkt, [1, 2])
            send_packet(dataplane, 1, pkt)
            verify_packets(dataplane, pkt, [0, 2])
            send_packet(dataplane, 2, pkt)
            verify_packets(dataplane, pkt, [0, 1])
    finally:
        for idx in range(3):
            npu.remove(vlan_mbr_oids[idx])
            npu.create_vlan_member(npu.default_vlan_oid, npu.dot1q_bp_oids[idx], "SAI_VLAN_TAGGING_MODE_UNTAGGED")
            npu.set(npu.port_oids[idx], ["SAI_PORT_ATTR_PORT_VLAN_ID", npu.default_vlan_id])
        npu.remove(vlan_oid)


def test_l2_lag(npu, dataplane):
    vlan_id = "10"
    macs = ['00:11:11:11:11:11', '00:22:22:22:22:22']
    max_port = 3
    lag_mbr_oids = []

    # Remove bridge ports
    for idx in range(max_port):
        npu.remove_vlan_member(npu.default_vlan_oid, npu.dot1q_bp_oids[idx])
        npu.remove(npu.dot1q_bp_oids[idx])

    # Remove Port #3 from the default VLAN
    npu.remove_vlan_member(npu.default_vlan_oid, npu.dot1q_bp_oids[3])

    # Create LAG
    lag_oid = npu.create(SaiObjType.LAG, [])

    # Create LAG members
    for idx in range(max_port):
        oid = npu.create(SaiObjType.LAG_MEMBER,
                         [
                             "SAI_LAG_MEMBER_ATTR_LAG_ID", lag_oid,
                             "SAI_LAG_MEMBER_ATTR_PORT_ID", npu.port_oids[idx]
                         ])
        lag_mbr_oids.append(oid)

    # Create bridge port for LAG
    lag_bp_oid = npu.create(SaiObjType.BRIDGE_PORT,
                            [
                                "SAI_BRIDGE_PORT_ATTR_TYPE", "SAI_BRIDGE_PORT_TYPE_PORT",
                                "SAI_BRIDGE_PORT_ATTR_PORT_ID", lag_oid,
                                #"SAI_BRIDGE_PORT_ATTR_BRIDGE_ID", npu.dot1q_br_oid,
                                "SAI_BRIDGE_PORT_ATTR_ADMIN_STATE", "true"
                            ])

    # Create VLAN
    vlan_oid = npu.create(SaiObjType.VLAN, ["SAI_VLAN_ATTR_VLAN_ID", vlan_id])

    # Create VLAN members
    npu.create_vlan_member(vlan_oid, lag_bp_oid, "SAI_VLAN_TAGGING_MODE_UNTAGGED")
    npu.create_vlan_member(vlan_oid, npu.dot1q_bp_oids[3], "SAI_VLAN_TAGGING_MODE_UNTAGGED")

    # Set PVID for LAG and Port #3
    npu.set(npu.port_oids[3], ["SAI_PORT_ATTR_PORT_VLAN_ID", vlan_id])
    npu.set(lag_oid, ["SAI_LAG_ATTR_PORT_VLAN_ID", vlan_id])

    npu.create_fdb(vlan_oid, macs[0], lag_bp_oid)
    npu.create_fdb(vlan_oid, macs[1], npu.dot1q_bp_oids[3])

    try:
        if npu.run_traffic:
            count = [0, 0, 0]
            dst_ip = int(socket.inet_aton('10.10.10.1').encode('hex'),16)
            max_itrs = 200
            for i in range(0, max_itrs):
                dst_ip_addr = socket.inet_ntoa(hex(dst_ip)[2:].zfill(8).decode('hex'))
                pkt = simple_tcp_packet(eth_dst=macs[0],
                                        eth_src=macs[1],
                                        ip_dst=dst_ip_addr,
                                        ip_src='192.168.8.1',
                                        ip_id=109,
                                        ip_ttl=64)

                send_packet(dataplane, 3, pkt)
                rcv_idx = verify_any_packet_any_port(dataplane, [pkt], [0, 1, 2])
                count[rcv_idx] += 1
                dst_ip += 1

            for i in range(0, 3):
                assert(count[i] >= ((max_itrs / 3) * 0.8))

            pkt = simple_tcp_packet(eth_src=macs[0],
                                    eth_dst=macs[1],
                                    ip_dst='10.0.0.1',
                                    ip_id=109,
                                    ip_ttl=64)

            print("Sending packet port 1 (lag member) -> port 4")
            send_packet(dataplane, 0, pkt)
            verify_packets(dataplane, pkt, [3])
            print("Sending packet port 2 (lag member) -> port 4")
            send_packet(dataplane, 1, pkt)
            verify_packets(dataplane, pkt, [3])
            print("Sending packet port 3 (lag member) -> port 4")
            send_packet(dataplane, 2, pkt)
            verify_packets(dataplane, pkt, [3])
    finally:
        npu.remove_fdb(vlan_oid, macs[0])
        npu.remove_fdb(vlan_oid, macs[1])

        npu.remove_vlan_member(vlan_oid, lag_bp_oid)
        npu.remove_vlan_member(vlan_oid, npu.dot1q_bp_oids[3])
        npu.remove(vlan_oid)

        for oid in lag_mbr_oids:
            npu.remove(oid)

        npu.remove(lag_bp_oid)
        npu.remove(lag_oid)

        # Create bridge port for ports removed from LAG
        for idx in range(max_port):
            bp_oid = npu.create(SaiObjType.BRIDGE_PORT,
                                [
                                    "SAI_BRIDGE_PORT_ATTR_TYPE", "SAI_BRIDGE_PORT_TYPE_PORT",
                                    "SAI_BRIDGE_PORT_ATTR_PORT_ID", npu.port_oids[idx],
                                    #"SAI_BRIDGE_PORT_ATTR_BRIDGE_ID", npu.dot1q_br_oid,
                                    "SAI_BRIDGE_PORT_ATTR_ADMIN_STATE", "true"
                                ])
            npu.dot1q_bp_oids[idx] = bp_oid

        # Add ports to default VLAN
        for oid in npu.dot1q_bp_oids[0:4]:
            npu.create_vlan_member(npu.default_vlan_oid, oid, "SAI_VLAN_TAGGING_MODE_UNTAGGED")

        # Set PVID
        for oid in npu.port_oids[0:4]:
            npu.set(oid, ["SAI_PORT_ATTR_PORT_VLAN_ID", npu.default_vlan_id])


def test_l2_vlan_bcast_ucast(npu, dataplane):
    vlan_id = "10"
    macs = []

    # Create VLAN
    vlan_oid = npu.create(SaiObjType.VLAN, ["SAI_VLAN_ATTR_VLAN_ID", vlan_id])

    for idx, bp_oid in enumerate(npu.dot1q_bp_oids):
        npu.remove_vlan_member(npu.default_vlan_oid, bp_oid)
        npu.create_vlan_member(vlan_oid, bp_oid, "SAI_VLAN_TAGGING_MODE_UNTAGGED")
        npu.set(npu.port_oids[idx], ["SAI_PORT_ATTR_PORT_VLAN_ID", vlan_id])

        macs.append("00:00:00:00:00:%02x" %(idx+1))
        npu.create_fdb(vlan_oid, macs[idx], bp_oid)

    try:
        if npu.run_traffic:
            bcast_pkt = simple_tcp_packet(eth_dst='ff:ff:ff:ff:ff:ff',
                                          eth_src='00:00:00:00:00:01',
                                          ip_dst='10.0.0.1',
                                          ip_id=101,
                                          ip_ttl=64)

            expected_ports = []
            for idx in range(len(npu.dot1q_bp_oids)):
                expected_ports.append(idx)

            send_packet(dataplane, 0, bcast_pkt)
            verify_packets(dataplane, bcast_pkt, expected_ports)

            for idx, mac in enumerate(macs):
                ucast_pkt = simple_tcp_packet(eth_dst=mac,
                                              eth_src='00:00:00:00:00:01',
                                              ip_dst='10.0.0.1',
                                              ip_id=101,
                                              ip_ttl=64)

                send_packet(dataplane, 0, ucast_pkt)
                verify_packets(dataplane, ucast_pkt, [idx])

    finally:
        for idx, bp_oid in enumerate(npu.dot1q_bp_oids):
            npu.remove_fdb(vlan_oid, macs[idx])
            npu.remove_vlan_member(vlan_oid, bp_oid)
            npu.create_vlan_member(npu.default_vlan_oid, bp_oid, "SAI_VLAN_TAGGING_MODE_UNTAGGED")
            npu.set(npu.port_oids[idx], ["SAI_PORT_ATTR_PORT_VLAN_ID", npu.default_vlan_id])
        npu.remove(vlan_oid)


def test_l2_mtu(npu, dataplane):
    vlan_id = "10"
    port_mtu = "1500"
    port_default_mtu = []
    max_port = 3

    for oid in npu.port_oids[0:max_port]:
        mtu = npu.get(oid, ["SAI_PORT_ATTR_MTU", ""]).value()
        port_default_mtu.append(mtu)

    for oid in npu.dot1q_bp_oids[0:max_port]:
        npu.remove_vlan_member(npu.default_vlan_oid, oid)

    vlan_oid = npu.create(SaiObjType.VLAN, ["SAI_VLAN_ATTR_VLAN_ID", vlan_id])

    npu.create_vlan_member(vlan_oid, npu.dot1q_bp_oids[0], "SAI_VLAN_TAGGING_MODE_UNTAGGED")
    npu.create_vlan_member(vlan_oid, npu.dot1q_bp_oids[1], "SAI_VLAN_TAGGING_MODE_UNTAGGED")
    npu.create_vlan_member(vlan_oid, npu.dot1q_bp_oids[2], "SAI_VLAN_TAGGING_MODE_TAGGED")

    for oid in npu.port_oids[0:max_port]:
        npu.set(oid, ["SAI_PORT_ATTR_MTU", port_mtu])
        npu.set(oid, ["SAI_PORT_ATTR_PORT_VLAN_ID", vlan_id])

    try:
        if npu.run_traffic:
            pkt = simple_tcp_packet(pktlen=1400,
                                    eth_dst='00:22:22:22:22:22',
                                    eth_src='00:11:11:11:11:11',
                                    ip_dst='10.0.0.1',
                                    ip_id=101,
                                    ip_ttl=64)

            tag_pkt = simple_tcp_packet(pktlen=1404,
                                        eth_dst='00:22:22:22:22:22',
                                        eth_src='00:11:11:11:11:11',
                                        dl_vlan_enable=True,
                                        vlan_vid=vlan_id,
                                        ip_dst='10.0.0.1',
                                        ip_id=101,
                                        ip_ttl=64)

            pkt1 = simple_tcp_packet(pktlen=1500,
                                     eth_dst='00:22:22:22:22:22',
                                     eth_src='00:11:11:11:11:11',
                                     ip_dst='10.0.0.1',
                                     ip_id=101,
                                     ip_ttl=64)

            tag_pkt1 = simple_tcp_packet(pktlen=1504,
                                         eth_dst='00:22:22:22:22:22',
                                         eth_src='00:11:11:11:11:11',
                                         dl_vlan_enable=True,
                                         vlan_vid=vlan_id,
                                         ip_dst='10.0.0.1',
                                         ip_id=101,
                                         ip_ttl=64)

            send_packet(dataplane, 0, pkt)
            verify_packet(dataplane, pkt, 1)
            verify_packet(dataplane, tag_pkt, 2)

            send_packet(dataplane, 0, pkt1)
            verify_packet(dataplane, pkt1, 1)
            verify_no_packet(dataplane, tag_pkt1, 2)

    finally:
        for idx, oid in enumerate(npu.port_oids[0:max_port]):
            npu.remove_vlan_member(vlan_oid, npu.dot1q_bp_oids[idx])
            npu.create_vlan_member(npu.default_vlan_oid, npu.dot1q_bp_oids[idx], "SAI_VLAN_TAGGING_MODE_UNTAGGED")
            npu.set(oid, ["SAI_PORT_ATTR_PORT_VLAN_ID", npu.default_vlan_id])
            npu.set(oid, ["SAI_PORT_ATTR_MTU", port_default_mtu[idx]])
        npu.remove(vlan_oid)


def test_fdb_bulk_create(npu, dataplane):
    macs = ['00:11:11:11:11:11', '00:22:22:22:22:22',
            '00:33:33:33:33:33', '00:44:44:44:44:44']
    entry = {
        "bvid"      : npu.default_vlan_oid,
        "switch_id" : npu.oid,
    }

    keys = []
    for mac in macs:
        entry["mac"] = mac
        keys.append(entry.copy())

    attrs = []
    attrs.append("SAI_FDB_ENTRY_ATTR_TYPE")
    attrs.append("SAI_FDB_ENTRY_TYPE_STATIC")
    attrs.append("SAI_FDB_ENTRY_ATTR_BRIDGE_PORT_ID")
    attrs.append(npu.dot1q_bp_oids[0])

    npu.bulk_create(SaiObjType.FDB_ENTRY, keys, [attrs])

    try:
        if npu.run_traffic:
            src_mac = '00:00:00:11:22:33'
            dst_mac = '00:00:00:aa:bb:cc'

            # Check no flooding for created FDB entries
            for mac in macs:
                pkt = simple_tcp_packet(eth_dst=mac, eth_src=src_mac)
                send_packet(dataplane, 1, pkt)
                verify_packets(dataplane, pkt, [0])

            # Check flooding if no FDB entry
            pkt = simple_tcp_packet(eth_dst=dst_mac, eth_src=src_mac)
            send_packet(dataplane, 1, pkt)
            egress_ports = list(range(len(npu.port_oids)))
            egress_ports.remove(1)
            verify_packets(dataplane, pkt, egress_ports)
    finally:
        npu.flush_fdb_entries(["SAI_FDB_FLUSH_ATTR_BV_ID", npu.default_vlan_oid])


def test_fdb_bulk_remove(npu, dataplane):
    src_mac = '00:00:00:11:22:33'
    macs = ['00:11:11:11:11:11', '00:22:22:22:22:22',
            '00:33:33:33:33:33', '00:44:44:44:44:44']

    for mac in macs:
        npu.create_fdb(npu.default_vlan_oid, mac, npu.dot1q_bp_oids[0])

    try:
        if npu.run_traffic:
            # Check no flooding for created FDB entries
            for mac in macs:
                pkt = simple_tcp_packet(eth_dst=mac, eth_src=src_mac)
                send_packet(dataplane, 1, pkt)
                verify_packets(dataplane, pkt, [0])

        # Bulk remove FDB entries
        keys = []
        entry = {
            "bvid"      : npu.default_vlan_oid,
            "switch_id" : npu.oid,
        }
        for mac in macs:
            entry["mac"] = mac
            keys.append(entry.copy())

        npu.bulk_remove(SaiObjType.FDB_ENTRY, keys)

        if npu.run_traffic:
            # Check flooding if no FDB entry
            egress_ports = list(range(len(npu.port_oids)))
            egress_ports.remove(1)
            for mac in macs:
                pkt = simple_tcp_packet(eth_dst=mac, eth_src=src_mac)
                send_packet(dataplane, 1, pkt)
                verify_packets(dataplane, pkt, egress_ports)

    finally:
        npu.flush_fdb_entries(["SAI_FDB_FLUSH_ATTR_BV_ID", npu.default_vlan_oid])
