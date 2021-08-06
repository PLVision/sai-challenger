import pytest
from sai import SaiObjType

rif_attrs = [
    ("SAI_ROUTER_INTERFACE_ATTR_VIRTUAL_ROUTER_ID",             "sai_object_id_t"),
    ("SAI_ROUTER_INTERFACE_ATTR_TYPE",                          "sai_router_interface_type_t"),
    ("SAI_ROUTER_INTERFACE_ATTR_PORT_ID",                       "sai_object_id_t"),
    ("SAI_ROUTER_INTERFACE_ATTR_VLAN_ID",                       "sai_object_id_t"),
    ("SAI_ROUTER_INTERFACE_ATTR_SRC_MAC_ADDRESS",               "sai_mac_t"),
    ("SAI_ROUTER_INTERFACE_ATTR_ADMIN_V4_STATE",                "bool"),
    ("SAI_ROUTER_INTERFACE_ATTR_ADMIN_V6_STATE",                "bool"),
    ("SAI_ROUTER_INTERFACE_ATTR_MTU",                           "sai_uint32_t"),
    ("SAI_ROUTER_INTERFACE_ATTR_INGRESS_ACL",                   "sai_object_id_t"),
    ("SAI_ROUTER_INTERFACE_ATTR_EGRESS_ACL",                    "sai_object_id_t"),
    ("SAI_ROUTER_INTERFACE_ATTR_NEIGHBOR_MISS_PACKET_ACTION",   "sai_packet_action_t"),
    ("SAI_ROUTER_INTERFACE_ATTR_V4_MCAST_ENABLE",               "bool"),
    ("SAI_ROUTER_INTERFACE_ATTR_V6_MCAST_ENABLE",               "bool"),
    ("SAI_ROUTER_INTERFACE_ATTR_LOOPBACK_PACKET_ACTION",        "sai_packet_action_t"),
    ("SAI_ROUTER_INTERFACE_ATTR_IS_VIRTUAL",                    "bool"),
    ("SAI_ROUTER_INTERFACE_ATTR_NAT_ZONE_ID",                   "sai_uint8_t"),
    ("SAI_ROUTER_INTERFACE_ATTR_DISABLE_DECREMENT_TTL",         "bool"),
    ("SAI_ROUTER_INTERFACE_ATTR_ADMIN_MPLS_STATE",              "bool")
]

rif_attrs_default = {}
rif_attrs_updated = {}


@pytest.fixture(scope="module")
def sai_rif_obj_port(npu):
    vrf_oid1 = npu.create(SaiObjType.VIRTUAL_ROUTER, [])
    rif_oid = npu.create(SaiObjType.ROUTER_INTERFACE,
                         [
                             'SAI_ROUTER_INTERFACE_ATTR_TYPE', 'SAI_ROUTER_INTERFACE_TYPE_PORT',
                             'SAI_ROUTER_INTERFACE_ATTR_PORT_ID', npu.port_oids[0],
                             'SAI_ROUTER_INTERFACE_ATTR_VIRTUAL_ROUTER_ID', vrf_oid1
                         ])
    yield rif_oid
    npu.remove(rif_oid)


@pytest.fixture(scope="module")
def sai_rif_obj_vlan(npu):
    vlan_oid = npu.create(SaiObjType.VLAN, ["SAI_VLAN_ATTR_VLAN_ID", "10"])
    vrf_oid1 = npu.create(SaiObjType.VIRTUAL_ROUTER, [])
    rif_oid = npu.create(SaiObjType.ROUTER_INTERFACE,
                         [
                             'SAI_ROUTER_INTERFACE_ATTR_TYPE', 'SAI_ROUTER_INTERFACE_TYPE_VLAN',
                             'SAI_ROUTER_INTERFACE_ATTR_VLAN_ID', vlan_oid,
                             'SAI_ROUTER_INTERFACE_ATTR_VIRTUAL_ROUTER_ID', vrf_oid1
                         ])
    yield rif_oid
    npu.remove(rif_oid)
    npu.remove(vrf_oid1)
    npu.remove(vlan_oid)


@pytest.mark.parametrize(
    "attr,attr_type",
    rif_attrs
)
def test_get_before_set_attr_port(npu, dataplane, sai_rif_obj_port, attr, attr_type):
    status, data = npu.get_by_type(sai_rif_obj_port, attr, attr_type, do_assert=False)
    npu.assert_status_success(status)
    if status == "SAI_STATUS_SUCCESS":
        rif_attrs_default[attr] = data.value()


@pytest.mark.parametrize(
    "attr,attr_type",
    rif_attrs
)
def test_get_before_set_attr_vlan(npu, dataplane, sai_rif_obj_vlan, attr, attr_type):
    status, data = npu.get_by_type(sai_rif_obj_vlan, attr, attr_type, do_assert=False)
    npu.assert_status_success(status)
    if status == "SAI_STATUS_SUCCESS":
        rif_attrs_default[attr] = data.value()


valued_attr = [
    ("SAI_ROUTER_INTERFACE_ATTR_TYPE",                              "SAI_ROUTER_INTERFACE_TYPE_PORT"),
    ("SAI_ROUTER_INTERFACE_ATTR_TYPE",                              "SAI_ROUTER_INTERFACE_TYPE_VLAN"),
    ("SAI_ROUTER_INTERFACE_ATTR_PORT_ID",                           "oid:0x0"),
    ("SAI_ROUTER_INTERFACE_ATTR_VLAN_ID",                           "oid:0x0"),
    ("SAI_ROUTER_INTERFACE_ATTR_SRC_MAC_ADDRESS",                   "00:11:11:11:11:11"),
    ("SAI_ROUTER_INTERFACE_ATTR_ADMIN_V4_STATE",                    "true"),
    ("SAI_ROUTER_INTERFACE_ATTR_ADMIN_V4_STATE",                    "false"),
    ("SAI_ROUTER_INTERFACE_ATTR_ADMIN_V6_STATE",                    "true"),
    ("SAI_ROUTER_INTERFACE_ATTR_ADMIN_V6_STATE",                    "false"),
    ("SAI_ROUTER_INTERFACE_ATTR_MTU",                               "1500"),
    ("SAI_ROUTER_INTERFACE_ATTR_INGRESS_ACL",                       "oid:0x0"),
    ("SAI_ROUTER_INTERFACE_ATTR_EGRESS_ACL",                        "oid:0x0"),
    ("SAI_ROUTER_INTERFACE_ATTR_NEIGHBOR_MISS_PACKET_ACTION",       "SAI_PACKET_ACTION_DROP"),
    ("SAI_ROUTER_INTERFACE_ATTR_NEIGHBOR_MISS_PACKET_ACTION",       "SAI_PACKET_ACTION_FORWARD"),
    ("SAI_ROUTER_INTERFACE_ATTR_NEIGHBOR_MISS_PACKET_ACTION",       "SAI_PACKET_ACTION_COPY"),
    ("SAI_ROUTER_INTERFACE_ATTR_NEIGHBOR_MISS_PACKET_ACTION",       "SAI_PACKET_ACTION_COPY_CANCEL"),
    ("SAI_ROUTER_INTERFACE_ATTR_NEIGHBOR_MISS_PACKET_ACTION",       "SAI_PACKET_ACTION_TRAP"),
    ("SAI_ROUTER_INTERFACE_ATTR_NEIGHBOR_MISS_PACKET_ACTION",       "SAI_PACKET_ACTION_LOG"),
    ("SAI_ROUTER_INTERFACE_ATTR_NEIGHBOR_MISS_PACKET_ACTION",       "SAI_PACKET_ACTION_DENY"),
    ("SAI_ROUTER_INTERFACE_ATTR_NEIGHBOR_MISS_PACKET_ACTION",       "SAI_PACKET_ACTION_TRANSIT"),
    ("SAI_ROUTER_INTERFACE_ATTR_V4_MCAST_ENABLE",                   "true"),
    ("SAI_ROUTER_INTERFACE_ATTR_V4_MCAST_ENABLE",                   "false"),
    ("SAI_ROUTER_INTERFACE_ATTR_V6_MCAST_ENABLE",                   "true"),
    ("SAI_ROUTER_INTERFACE_ATTR_V6_MCAST_ENABLE",                   "false"),
    ("SAI_ROUTER_INTERFACE_ATTR_LOOPBACK_PACKET_ACTION",            "SAI_PACKET_ACTION_DROP"),
    ("SAI_ROUTER_INTERFACE_ATTR_LOOPBACK_PACKET_ACTION",            "SAI_PACKET_ACTION_FORWARD"),
    ("SAI_ROUTER_INTERFACE_ATTR_LOOPBACK_PACKET_ACTION",            "SAI_PACKET_ACTION_COPY"),
    ("SAI_ROUTER_INTERFACE_ATTR_LOOPBACK_PACKET_ACTION",            "SAI_PACKET_ACTION_COPY_CANCEL"),
    ("SAI_ROUTER_INTERFACE_ATTR_LOOPBACK_PACKET_ACTION",            "SAI_PACKET_ACTION_TRAP"),
    ("SAI_ROUTER_INTERFACE_ATTR_LOOPBACK_PACKET_ACTION",            "SAI_PACKET_ACTION_LOG"),
    ("SAI_ROUTER_INTERFACE_ATTR_LOOPBACK_PACKET_ACTION",            "SAI_PACKET_ACTION_DENY"),
    ("SAI_ROUTER_INTERFACE_ATTR_LOOPBACK_PACKET_ACTION",            "SAI_PACKET_ACTION_TRANSIT"),
    ("SAI_ROUTER_INTERFACE_ATTR_IS_VIRTUAL",                        "true"),
    ("SAI_ROUTER_INTERFACE_ATTR_IS_VIRTUAL",                        "false"),
    ("SAI_ROUTER_INTERFACE_ATTR_NAT_ZONE_ID",                       "2"),
    ("SAI_ROUTER_INTERFACE_ATTR_DISABLE_DECREMENT_TTL",             "true"),
    ("SAI_ROUTER_INTERFACE_ATTR_DISABLE_DECREMENT_TTL",             "false"),
    ("SAI_ROUTER_INTERFACE_ATTR_ADMIN_MPLS_STATE",                  "true"),
    ("SAI_ROUTER_INTERFACE_ATTR_ADMIN_MPLS_STATE",                  "false")
]


@pytest.mark.parametrize(
    "attr,attr_value",
    valued_attr
)
def test_set_attr_port(npu, dataplane, sai_rif_obj_port, attr, attr_value):
    status = npu.set(sai_rif_obj_port, [attr, attr_value], False)
    npu.assert_status_success(status)
    if status == "SAI_STATUS_SUCCESS":
        rif_attrs_updated[attr] = attr_value


@pytest.mark.parametrize(
    "attr,attr_value",
    valued_attr
)
def test_set_attr_vlan(npu, dataplane, sai_rif_obj_vlan, attr, attr_value):
    status = npu.set(sai_rif_obj_vlan, [attr, attr_value], False)
    npu.assert_status_success(status)
    if status == "SAI_STATUS_SUCCESS":
        rif_attrs_updated[attr] = attr_value


rif_attrs = [
    ("SAI_ROUTER_INTERFACE_ATTR_SRC_MAC_ADDRESS",               "sai_mac_t"),
    ("SAI_ROUTER_INTERFACE_ATTR_ADMIN_V4_STATE",                "bool"),
    ("SAI_ROUTER_INTERFACE_ATTR_ADMIN_V6_STATE",                "bool"),
    ("SAI_ROUTER_INTERFACE_ATTR_MTU",                           "sai_uint32_t"),
    ("SAI_ROUTER_INTERFACE_ATTR_INGRESS_ACL",                   "sai_object_id_t"),
    ("SAI_ROUTER_INTERFACE_ATTR_EGRESS_ACL",                    "sai_object_id_t"),
    ("SAI_ROUTER_INTERFACE_ATTR_NEIGHBOR_MISS_PACKET_ACTION",   "sai_packet_action_t"),
    ("SAI_ROUTER_INTERFACE_ATTR_V4_MCAST_ENABLE",               "bool"),
    ("SAI_ROUTER_INTERFACE_ATTR_V6_MCAST_ENABLE",               "bool"),
    ("SAI_ROUTER_INTERFACE_ATTR_LOOPBACK_PACKET_ACTION",        "sai_packet_action_t"),
    ("SAI_ROUTER_INTERFACE_ATTR_IS_VIRTUAL",                    "bool"),  # !
    ("SAI_ROUTER_INTERFACE_ATTR_NAT_ZONE_ID",                   "sai_uint8_t"),
    ("SAI_ROUTER_INTERFACE_ATTR_DISABLE_DECREMENT_TTL",         "bool"),
    ("SAI_ROUTER_INTERFACE_ATTR_ADMIN_MPLS_STATE",              "bool"),
]


@pytest.mark.parametrize(
    "attr,attr_type",
    rif_attrs
)
def test_get_after_set_attr_port(npu, dataplane, sai_rif_obj_port, attr, attr_type):
    status, data = npu.get_by_type(sai_rif_obj_vlan, attr, attr_type, do_assert=False)
    npu.assert_status_success(status)


@pytest.mark.parametrize(
    "attr,attr_type",
    rif_attrs
)
def test_get_after_set_attr_vlan(npu, dataplane, sai_rif_obj_vlan, attr, attr_type):
    status, data = npu.get_by_type(sai_rif_obj_vlan, attr, attr_type, do_assert=False)
    npu.assert_status_success(status)
