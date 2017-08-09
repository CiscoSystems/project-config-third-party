#!/bin/bash -xe

# Copyright (C) 2014 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.

# We need to ensure that we can find utilities like ip and restorecon
# which at least on some distros live in /usr/sbin.
export PATH="$PATH:/sbin:/usr/sbin:/bin:/usr/bin:/usr/local/bin"

if [ -f /etc/dib-builddate.txt ]; then
    echo "Image build date"
    echo "================"
    cat /etc/dib-builddate.txt
fi

LSBDISTID=$(lsb_release -is)
LSBDISTCODENAME=$(lsb_release -cs)

# Double check that when the node is made ready it is able
# to resolve names against DNS.
# NOTE(pabelanger): Because it is possible for nodepool to SSH into a node but
# DNS has not been fully started, we try up to 300 seconds (10 attempts) to
# resolve DNS once.
for COUNT in {1..10}; do
    set +e
    host -W 30 git.openstack.org
    res=$?
    set -e
    if [ $res == 0 ]; then
        break
    elif [ $COUNT == 10 ]; then
        exit 1
    fi
done

if [ "$LSBDISTID" == "Debian" ] || [ "$LSBDISTID" == "Ubuntu" ]; then
    # Make sure our indexes are up to date.
    sudo apt-get update
    sudo apt-get install default-jdk
fi
