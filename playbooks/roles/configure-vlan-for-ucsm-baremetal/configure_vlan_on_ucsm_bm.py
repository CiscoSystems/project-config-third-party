import argparse
from ucsmsdk.ucshandle import UcsHandle
from ucsmsdk.mometa.vnic.VnicEtherIf import VnicEtherIf
from ucsmsdk.mometa.fabric.FabricVlan import FabricVlan

parser = argparse.ArgumentParser()
parser.add_argument('ucsm_ip')
parser.add_argument('username')
parser.add_argument('password')
parser.add_argument('sp_name')
parser.add_argument('vlan')
parser.add_argument('--remove', action='store_true',
                    help=("Remove the service profile with name"))


def connect_to_ucsm(args):
    handle = UcsHandle(args.ucsm_ip, args.username, args.password)
    handle.login()
    return handle


def assign_vlan_to_sp_vnic(handle, args):
    # Remove any existing ironic-<vlan> vifs from this UCSM server
    existing_ironic_vifs = handle.query_classid(
        'VnicEtherIf',
        filter_str=(
            '(name, ".*ironic-.*") and (dn, ".*{0}.*")'.format(args.sp_name))
    )
    for vif in existing_ironic_vifs:
        handle.remove_mo(vif)
    handle.commit()

    # Add the vlan to UCSM globally if it doesn't already exist
    vlan = handle.query_dn('fabric/lan/net-ironic-{0}'.format(args.vlan))
    if not vlan:
        vp1 = handle.query_dn("fabric/lan")
        handle.add_mo(FabricVlan(vp1, name="ironic-{0}".format(args.vlan),
                                 id=args.vlan))
        handle.commit()

    # Add the the VLAN as the default network for the first NIC on the server
    eth0 = handle.query_classid(
        'VnicEther', filter_str='(dn, ".*{0}.*")'.format(args.sp_name))[0]
    VnicEtherIf(parent_mo_or_dn=eth0, default_net="yes",
                name="ironic-{0}".format(args.vlan))
    handle.set_mo(eth0)
    handle.commit()


if __name__ == '__main__':
    args = parser.parse_args()
    handle = connect_to_ucsm(args)
    assign_vlan_to_sp_vnic(handle, args)
