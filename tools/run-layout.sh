#!/bin/bash -e

# Copyright 2013 OpenStack Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

config=$(readlink -f tools/jenkins.ini)

mkdir -p .test
cd .test
[ -d zuul ] || git clone https://git.openstack.org/openstack-infra/zuul --depth 1 -b 2.6.0
[ -d jenkins-job-builder ] || git clone https://git.openstack.org/openstack-infra/jenkins-job-builder --depth 1 -b 1.6.2
cd jenkins-job-builder
# These are $WORKSPACE/.test/jenkins-job-builder/.test/...
mkdir -p .test/new/config
mkdir -p .test/new/out
cd ../..

cp jenkins/jobs/* .test/jenkins-job-builder/.test/new/config
cd .test/jenkins-job-builder
tox -e compare-xml-config -- --conf $config test -o .test/new/out/ .test/new/config/

cd ..
find jenkins-job-builder/.test/new/out/ -exec basename {} \; > job-list.txt

cd zuul
tox -e venv -- zuul-server -c etc/zuul.conf-sample -l ../../zuul/layout.yaml -t ../job-list.txt
