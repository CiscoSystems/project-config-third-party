import argparse
import sys
from ucsmsdk.ucshandle import UcsHandle
from ucsmsdk.mometa.ls.LsServer import LsServer
from ucsmsdk.mometa.vnic.VnicEther import VnicEther
from ucsmsdk.mometa.vnic.VnicEtherIf import VnicEtherIf
from ucsmsdk.mometa.vnic.VnicFcNode import VnicFcNode


parser = argparse.ArgumentParser()
parser.add_argument('sp_name')
parser.add_argument('--remove', action='store_true',
                    help=("Remove the service profile with name"))

UCSM_IP = "192.133.149.20"
UCSM_USERNAME = "admin"
UCSM_PASSWORD = "Cisc0123"


def connect_to_ucsm():
    handle = UcsHandle(UCSM_IP, UCSM_USERNAME, UCSM_PASSWORD)
    handle.login()
    return handle


def create_service_profile(name, handle):
    # Service Profile
    sp = LsServer(parent_mo_or_dn="org-root", name=name)
    # Vnic eth0
    vnic_eth0 = VnicEther(parent_mo_or_dn=sp, name="eth0")
    VnicEtherIf(parent_mo_or_dn=vnic_eth0, default_net="yes", name="default")
    # Vnic eth1
    vnic_eth1 = VnicEther(parent_mo_or_dn=sp, name="eth1")
    VnicEtherIf(parent_mo_or_dn=vnic_eth1, default_net="yes", name="default")
    VnicFcNode(parent_mo_or_dn=sp, ident_pool_name="", addr="pool-derived")
    handle.add_mo(sp)
    try:
        handle.commit()
    except:
        print "Error creating Service Profile"
        sys.exit(1)
    handle.logout()


def remove_service_profile(name, handle):
    filter_str = '(name, "' + name + '")'
    sp = handle.query_classid(class_id="LsServer", filter_str=filter_str)
    try:
        handle.remove_mo(sp[0])
        handle.commit()
    except:
        print "Error removing Service Profile"
        sys.exit(1)
    handle.logout()

if __name__ == '__main__':
    args = parser.parse_args()

    if not args.sp_name:
        sys.exit(1)

    handle = connect_to_ucsm()
    if args.remove:
        remove_service_profile(args.sp_name, handle)
    else:
        create_service_profile(args.sp_name, handle)
