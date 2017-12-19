import argparse
import paramiko
import sys


parser = argparse.ArgumentParser()
parser.add_argument('address')
parser.add_argument('username')
parser.add_argument('password')
parser.add_argument('interface_number', metavar='interface-number')
parser.add_argument('vlanstart', metavar='vlan-start')
parser.add_argument('vlanend', metavar='vlan-end')
parser.add_argument('vlannative', nargs='?', metavar='native-vlan')
parser.add_argument('--remove', action='store_true',
                    help=("Remove the vlan configurations instead of "
                          "adding them to the nexus switch"))

# NOTE(sambetts) Ensure that a space is left before and after the semicolon to
# ensure nexus parses the commands correctly.
MAIN_TEMPLATE = (
    "config terminal ; "
    "{no}vlan {0.vlanstart}-{0.vlanend} ; "
    "interface Ethernet {0.interface_number} ; "
    "switchport mode trunk ; "
    "switchport trunk allowed vlan {op} {0.vlanstart}-{0.vlanend} ; ")

NATIVE_TEMPLATE = "{no}switchport trunk native vlan {0.vlannative} ;"


def set_nexus_config(args):
    client = paramiko.client.SSHClient()
    client.load_system_host_keys()
    client.connect(args.address, username=args.username,
                   password=args.password)

    no = ''
    op = 'add'
    if args.remove:
        no = 'no '
        op = 'remove'

    template = MAIN_TEMPLATE
    if args.vlannative:
        template += NATIVE_TEMPLATE

    cmd = template.format(args, no=no, op=op)
    print("Running command: %s" % cmd)

    stdin, stdout, stderr = client.exec_command(cmd)

    output = ""
    for line in stdout.readlines():
        output += line
    print("Nexus switch returned:")
    print(output)

    client.close()

    if "error" in output:
        sys.exit(1)


if __name__ == '__main__':
    args = parser.parse_args()
    set_nexus_config(args)
