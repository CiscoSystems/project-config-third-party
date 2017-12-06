import os
import paramiko
import sys

nexus_ip = os.environ.get('NEXUS_IP')
nexus_user = os.environ.get('NEXUS_USER')
nexus_password = os.environ.get('NEXUS_PASSWORD')
nexus_intf_num = os.environ.get('NEXUS_INTF_NUM')
nexus_vlan_start = os.environ.get('NEXUS_VLAN_START')
nexus_vlan_end = os.environ.get('NEXUS_VLAN_END')


def set_nexus_config(ip, user, password, op, intf_num, vlan_start, vlan_end,
                     vlan_native=None):
    client = paramiko.client.SSHClient()
    client.load_system_host_keys()
    client.connect(ip, username=user, password=password)

    cmd = 'config terminal ; '
    if op == 'remove':
        cmd += 'no '
    cmd += ('vlan {0}-{1} ; ').format(vlan_start, vlan_end)
    cmd += ('interface Ethernet {0} ; '
            'switchport mode trunk ;'
            'switchport trunk allowed vlan {3} {1}-{2} ; '
            ).format(intf_num, vlan_start, vlan_end, op)

    if vlan_native:
        if op == 'remove':
            cmd += 'no '
        cmd += ('switchport trunk native vlan {0}').format(vlan_native)

    print cmd
    stdin, stdout, stderr = client.exec_command(cmd)
    print stdout.readlines()
    client.close()


def print_usage():
    print "Usage:"
    print "    python %s <nexus-ip> <user> <password> " \
        "[add|remove]" % sys.argv[0]
    print "              <intf-num> <vlan-start> <vlan-end> <vlan-native>"
    print "Example:"
    print "    python %s 10.0.1.32 admin MyPassword add 1/9 810 813" % \
        sys.argv[0]
    print "Note: VLAN range is inclusive."
    print "Note: Number of VLANs in VLAN range should not exceed 100."

if __name__ == '__main__':
    if "--help" in sys.argv:
        print_usage()
        sys.exit(0)
    min_args = 8
    max_args = 9
    if (len(sys.argv) < min_args or
            len(sys.argv) > max_args):
        print_usage()
        sys.exit(1)
    ip = sys.argv[1]
    user = sys.argv[2]
    passwd = sys.argv[3]
    op = sys.argv[4]
    intf = sys.argv[5]
    min_vlan = sys.argv[6]
    max_vlan = sys.argv[7]
    if len(sys.argv) == min_args:
        set_nexus_config(ip, user, passwd, op, intf, min_vlan, max_vlan)
    if len(sys.argv) >= min_args + 1:
        native_vlan = sys.argv[min_args]
        set_nexus_config(ip, user, passwd, op, intf, min_vlan,
                         max_vlan, native_vlan)
