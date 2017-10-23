#!/usr/bin/env bash

#########################################################################
# This should run after the successful setup of a devstack environment to
# configured the node provider for use by the testing system
#########################################################################

# Keep track of the DevStack directory
TOP_DIR=$(cd $(dirname "$0") && pwd)

FULL_PROJECT_CONFIG_PATH=${FULL_PROJECT_CONFIG_PATH:-/home/rocket-man/project-config-third-party}

if [ -d "$FULL_PROJECT_CONFIG_PATH" ]; then
    echo "Could not run through local.sh because FULL_PROJECT_CONFIG_PATH is not set to a valid path"
    exit 0
fi

# Get OpenStack admin authentication
source $TOP_DIR/openrc admin admin

# Add an accessible IP address to the external bridge to allow node provider
# host to communicate in the OpenStack external network
sudo ip addr add 10.0.196.3/24 dev br-ex
sudo ip link set dev br-ex up

# Configure OpenStack security groups to allow the ports and protocols required
# for testing
security_group_id=$(openstack security group list --project demo -f value -c ID)
openstack security group rule create ${security_group_id} --proto gre
openstack security group rule create ${security_group_id} --proto gre --egress
openstack security group rule create ${security_group_id} --proto tcp --port 22
openstack security group rule create ${security_group_id} --proto icmp --port 0

security_group_id=$(openstack security group list --project demo -f value -c ID)
openstack security group rule create ${security_group_id} --proto gre
openstack security group rule create ${security_group_id} --proto gre --egress
openstack security group rule create ${security_group_id} --proto tcp --port 22
openstack security group rule create ${security_group_id} --proto icmp --port 0

# Configure flavor for use by the testing system
openstack flavor create Performance --ram 8192 --disk 30 --vcpus 4

# Setup next hop for external network for machine thats need to connect back to
# the jenkins host using its IP from the other network
openstack router set router1 --route destination=192.133.156.17/32,gateway=10.0.196.2

###########################################################################
# Setup a bridge VM for tunnelling L2 packet through to VMs that need to be
# artifically connected to a real switch.
###########################################################################

bridge_pub_ip=10.0.196.33
bridge_private_ip=10.0.0.24

# Setup local bridges on the physical NICs for the tunnels to connect too
sudo brctl addbr nexusint1
sudo brctl addbr nexusint2
sudo brctl addif nexusint1 enp9s0
sudo brctl addif nexusint2 enp10s0
sudo ip link set nexusint1 up
sudo ip link set nexusint2 up

# Create GRE tunnels and add them to the local bridges
sudo ip link add nexustap1 type gretap local 10.0.196.3 remote $bridge_pub_ip key 1
sudo ip link add nexustap2 type gretap local 10.0.196.3 remote $bridge_pub_ip key 2
sudo brctl addif nexusint1 nexustap1
sudo brctl addif nexusint2 nexustap2
sudo ip link set nexustap1 up
sudo ip link set nexustap2 up

# Create image used to boot the bridge-vm
export ELEMENTS_PATH=$FULL_PROJECT_CONFIG_PATH/nodepool/elements
export NODEPOOL_SCRIPTDIR=$FULL_PROJECT_CONFIG_PATH/nodepool/scripts
export NODEPOOL_STATIC_NAMESERVER_V4=208.67.222.222
export NODEPOOL_STATIC_NAMESERVER_V4_FALLBACK=208.67.220.220
export DIB_DEBIAN_COMPONENTS="main,universe"
export DIB_GRUB_TIMEOUT="0"
export DIB_DISABLE_APT_CLEANUP="1"
export DIB_APT_LOCAL_CACHE="0"
export DIB_CHECKSUM="1"
disk-image-create ubuntu-minimal vm simple-init nodepool-base initalize-urandom growroot infra-package-needs -o bridge-vm-image

# Upload image to glance for use
openstack image create --disk-format qcow2 --container-format bare --file bridge-vm-image.qcow2 bridge-vm-image

# Create keypair for communicating with the bridge VM
ssh-keygen -t rsa -N "" -f bridge-vm-setup-key
openstack keypair create --public-key bridge-vm-setup-key.pub bridge-vm-setup

# Create ports for the bridge VM
openstack port create --network private --fixed-ip ip-address=$bridge_private_ip bridge_private
openstack port create --network public --fixed-ip ip-address=$bridge_pub_ip bridge_public

# Create bridge VM to bridge the tunnels from the private network to the public
# network so that configuration on the node provider is static.
openstack server create --image bridge-vm-image --flavor Performance \
                        --key-name bridge-vm-setup --nic port-id=bridge_public \
                        --nic port-id=bridge_private --wait \
                        --config-drive=true nexus-bridge

# Run the playbook to setup and configure the bridge VM ready for use by the tests
ansible-playbook -i "$pub_ip," --private-key=bridge-vm-setup-key -u root -e $PATH_TO_PROJECT_CONFIG $PATH_TO_PROJECT_CONFIG/playbooks/bridge-vm-setup.yaml
