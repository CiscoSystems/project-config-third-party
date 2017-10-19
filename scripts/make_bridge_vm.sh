# Setup tapuser for SSH from the CI nodes
useradd tapuser
mkdir -p /home/tapuser/.ssh
chown -R tapuser:tapuser /home/tapuser
chmod 700 /home/tapuser/.ssh
cat project-config-third-party/nodepool/scripts/vm-bridge-key.pub > authorized_keys
chmod 600 /home/tapuser/.ssh/authorized_keys

# Install bridge utils
apt-get install bridge-utils

# Setup two bridges for L2 tunnels
brctl addbr nexusint1
brctl addbr nexusint2

# Setup GRE taps for the L2 tunnels to the node-provider
ip link add nexustap1 type gretap local 10.0.196.33 remote 10.0.196.3 key 1
ip link add nexustap2 type gretap local 10.0.196.33 remote 10.0.196.3 key 2

# Add GRE taps to the bridges
brctl addif nexusint1 nexustap1
brctl addif nexusint2 nexustap2

# insert -A openstack-INPUT -p gre -j ACCEPT into /etc/iptables/rules.v4
iptables-restore < /etc/iptables/rules.v4

# Setup bridges and taps state up
ip link set nexustap1 up
ip link set nexustap2 up
ip link set nexusint1 up
ip link set nexusint2 up

# Setup sudo for the tapuser to access brctl and ip commands
cat /etc/sudoers.d/tapuser << EOF
tapuser ALL=(ALL) NOPASSWD: /sbin/brctl
tapuser ALL=(ALL) NOPASSWD: /sbin/ip
EOF

# Setup OpenStack security groups for both internal network and
# external network
# openstack security group rule create <security group id> --proto gre
# openstack security group rule create <security group id> --proto gre --egress
