import inspect
import argparse
import logging
import re
import yaml

import xml.etree.ElementTree as ET
from networking_cisco.plugins.cisco.cfg_agent import cfg_exceptions as cfg_exc
from networking_cisco.plugins.cisco.cfg_agent.device_drivers.iosxe import (
    cisco_iosxe_snippets as snippets)
from networking_cisco.plugins.cisco.common.htparser import HTParser

from oslo_utils import importutils
ncclient = importutils.try_import('ncclient')
manager = importutils.try_import('ncclient.manager')

# MUCH of this code is essentially duplicated from iosxe_routing_driver
# - it was depending on a lot of imports that didn't seem easy to resolve in
#   standalone env with no neutron/neutron-lib installed.
#
# from networking_cisco.plugins.cisco.cfg_agent.device_drivers.iosxe import (
#    iosxe_routing_driver as iosxe_drvr)

logging.basicConfig()

LOG = logging.getLogger(__name__)

CFG_LINE_SNIPPET = """
<config>
        <cli-config-data>
            <cmd>%s</cmd>
        </cli-config-data>
</config>
"""


class CfgIosXe(object):
    def __init__(self, mgmtip, sshport, user, passwd, timeout=10):
        self._host_ip = mgmtip
        self._host_ssh_port = sshport
        self._username = user
        self._password = passwd
        self._timeout = timeout

        self._ncc_connection = None
        self._itfcs_enabled = False

        self._running_config = None

    def __del__(self):
        # clear the connection on destruction of this obj
        if self._ncc_connection and self._ncc_connection.connected:
            self._ncc_connection.close_session()

    def _get_connection(self):
        """Make SSH connection to the IOS XE device.

        The external ncclient library is used for creating this connection.
        This method keeps state of any existing connections and reuses them if
        already connected. Also interfaces (except management) are typically
        disabled by default when it is booted. So if connecting for the first
        time, driver will enable all other interfaces and keep that status in
        the `_itfcs_enabled` flag.
        """
        try:
            if self._ncc_connection and self._ncc_connection.connected:
                return self._ncc_connection
            else:
                # ncclient needs 'name' to be 'csr' in order to communicate
                # with the device in the correct way.
                self._ncc_connection = manager.connect(
                    host=self._host_ip, port=self._host_ssh_port,
                    username=self._username, password=self._password,
                    device_params={'name': "csr"}, timeout=self._timeout)
                if not self._itfcs_enabled:
                    self._itfcs_enabled = self._enable_itfcs(
                        self._ncc_connection)
            return self._ncc_connection
        except Exception as e:
            conn_params = {'host': self._host_ip, 'port': self._host_ssh_port,
                           'user': self._username,
                           'timeout': self._timeout, 'reason': e.message}
            raise cfg_exc.ConnectionException(**conn_params)

    def _enable_itfcs(self, conn):
        """Enable the interfaces of a IOS XE device.

        :param conn: Connection object
        :return: True or False
        """
        return True

    def _get_running_config(self, split=True):
        """Get the IOS XE device's current running config.

        :return: Current IOS running config as multiline string
        """
        if self._running_config:
            # cache the running config if we've gotten it already
            return self._running_config
        conn = self._get_connection()
        config = conn.get_config(source="running")
        if config:
            root = ET.fromstring(config._raw)
            running_config = root[0][0]
            if split is True:
                rgx = re.compile("\r*\n+")
                ioscfg = rgx.split(running_config.text)
            else:
                ioscfg = running_config.text
            self._running_config = ioscfg
            return ioscfg

    def caller_name(self, skip=2):
        """
        Get a name of a caller in the format module.class.method

       `skip` specifies how many levels of stack to skip while getting caller
       name. skip=1 means "who calls me", skip=2 "who calls my caller" etc.

       An empty string is returned if skipped levels exceed stack height
       """
        stack = inspect.stack()
        start = 0 + skip
        if len(stack) < start + 1:
            return ''
        parentframe = stack[start][0]

        name = []
        module = inspect.getmodule(parentframe)
        # `modname` can be None when frame is executed directly in console
        # TODO(asr1kteam): consider using __main__
        if module:
            name.append(module.__name__)
        # detect classname
        if 'self' in parentframe.f_locals:
            # I don't know any way to detect call from the object method
            # XXX: there seems to be no way to detect static method call,
            # it will be just a function call
            name.append(parentframe.f_locals['self'].__class__.__name__)
        codename = parentframe.f_code.co_name
        if codename != '<module>':  # top level usually
            name.append(codename)  # function or a method
        del parentframe
        return ".".join(name)

    def update_running_config(self):
        # clear the running config cache
        self._running_config = None

    def _edit_running_config(self, conf_str, snippet):
        conn = self._get_connection()
        LOG.info("Config generated for [%(device)s] %(snip)s is:%(conf)s "
                 "caller:%(caller)s",
                 {'device': self._host_ip,
                  'snip': snippet,
                  'conf': conf_str,
                  'caller': self.caller_name()})
        try:
            rpc_obj = conn.edit_config(target='running', config=conf_str)
            self._check_response(rpc_obj, snippet, conf_str=conf_str)
        except Exception as e:
            # Here we catch all exceptions caused by REMOVE_/DELETE_ configs
            # to avoid config agent to get stuck once it hits this condition.
            # This is needed since the current ncclient version (0.4.2)
            # generates an exception when an attempt to configure the device
            # fails by the device (ASR1K router) but it doesn't provide any
            # details about the error message that the device reported.
            # With ncclient 0.4.4 version and onwards the exception returns
            # also the proper error. Hence this code can be changed when the
            # ncclient version is increased.
            if re.search(r"REMOVE_|DELETE_", snippet):
                LOG.warning("Pass exception for %s", snippet)
                pass
            elif isinstance(e, ncclient.operations.rpc.RPCError):
                e_tag = e.tag
                e_type = e.type
                params = {'snippet': snippet, 'type': e_type, 'tag': e_tag,
                          'dev_id': self._host_ip,
                          'ip': self._host_ip, 'confstr': conf_str}
                raise cfg_exc.IOSXEConfigException(**params)

    def _check_response(self, rpc_obj, snippet_name, conf_str=None):
        """This function checks the rpc response object for status.

        This function takes as input the response rpc_obj and the snippet name
        that was executed. It parses it to see, if the last edit operation was
        a success or not.
            <?xml version="1.0" encoding="UTF-8"?>
            <rpc-reply message-id="urn:uuid:81bf8082-....-b69a-000c29e1b85c"
                       xmlns="urn:ietf:params:netconf:base:1.0">
                <ok />
            </rpc-reply>
        In case of error, IOS XE device sends a response as follows.
        We take the error type and tag.
            <?xml version="1.0" encoding="UTF-8"?>
            <rpc-reply message-id="urn:uuid:81bf8082-....-b69a-000c29e1b85c"
            xmlns="urn:ietf:params:netconf:base:1.0">
                <rpc-error>
                    <error-type>protocol</error-type>
                    <error-tag>operation-failed</error-tag>
                    <error-severity>error</error-severity>
                </rpc-error>
            </rpc-reply>
        :return: True if the config operation completed successfully
        :raises: networking_cisco.plugins.cisco.cfg_agent.cfg_exceptions.
        IOSXEConfigException
        """
        LOG.debug("RPCReply for %(snippet_name)s is %(rpc_obj)s",
                  {'snippet_name': snippet_name, 'rpc_obj': rpc_obj.xml})
        xml_str = rpc_obj.xml
        if "<ok />" in xml_str:
            # LOG.debug("RPCReply for %s is OK", snippet_name)
            LOG.info("%s was successfully executed", snippet_name)
            return True
        # Not Ok, we throw a ConfigurationException
        e_type = rpc_obj._root[0][0].text
        e_tag = rpc_obj._root[0][1].text
        params = {'snippet': snippet_name, 'type': e_type, 'tag': e_tag,
                  'dev_id': self._host_ip,
                  'ip': self._host_ip, 'confstr': conf_str}
        raise cfg_exc.IOSXEConfigException(**params)

    def _get_interfaces(self):
        """Get a list of interfaces on this hosting device.

        :return: List of the interfaces
        """
        ios_cfg = self._get_running_config()
        parse = HTParser(ios_cfg)
        itfcs_raw = parse.find_lines("^interface \w+\d+")
        itfcs = [raw_if.strip().split(' ')[1] for raw_if in itfcs_raw]
        LOG.debug("Interfaces on hosting device: %s", itfcs)
        return itfcs

    def _get_subinterfaces(self):
        """Get a list of subinterfaces on this hosting device.

        :return: List of the interfaces
        """
        ios_cfg = self._get_running_config()
        parse = HTParser(ios_cfg)
        itfcs_raw = parse.find_lines("^interface \w+\S+\.\d+")
        itfcs = [raw_if.strip().split(' ')[1] for raw_if in itfcs_raw]
        LOG.debug("subInterfaces on hosting device: %s", itfcs)
        return itfcs

    def _get_interfaces_objs(self):
        """Get a list of interfaces on this hosting device.

        :return: List of the interfaces' objects
        """
        ios_cfg = self._get_running_config()
        parse = HTParser(ios_cfg)
        itfcs_raw = parse.find_children("^interface \w+\d+")
        LOG.debug("Interfaces on hosting device: %s", itfcs_raw)
        return itfcs_raw

    def _get_interface_obj_children(self, intf):
        """Get a  interface's children on this hosting device.

        :return: List of the interfaces' objects
        """
        ios_cfg = self._get_running_config()
        parse = HTParser(ios_cfg)
        itfcs_raw = parse.find_children("^interface " + intf)
        LOG.debug("Interface children on hosting device: %s", itfcs_raw)
        return itfcs_raw

    def _get_regionid_subinterfaces(self, regionid):
        """Get a list of interfaces on this hosting device for the regionid.

        regionid

        :return: List of the interfaces' objects
        """
        intfs = self._get_subinterfaces()
        found_intfs = []
        for intf in intfs:
            intf_children = self._get_interface_obj_children(intf)
            print intf_children

            for child in intf_children:
                if re.search('description\s+.*' + regionid, child):
                    print "Found interface {intf}".format(intf=intf)
                    found_intfs.append(intf)
        return found_intfs

    def _get_vrfs(self):
        """Get the current VRFs configured in the device.

        :return: A list of vrf names as string
        """
        vrfs = []
        ios_cfg = self._get_running_config()
        parse = HTParser(ios_cfg)
        vrfs_raw = parse.find_lines("^vrf definition")
        for line in vrfs_raw:
            #  raw format ['ip vrf <vrf-name>',....]
            vrf_name = line.strip().split(' ')[2]
            vrfs.append(vrf_name)
        LOG.info("VRFs:%s", vrfs)
        return vrfs

    def _interface_exists(self, interface):
        """Check whether interface exists."""
        ios_cfg = self._get_running_config()
        parse = HTParser(ios_cfg)
        itfcs_raw = parse.find_lines("^interface " + interface)
        return len(itfcs_raw) > 0

    def _do_remove_vrf(self, vrf_name):
        if vrf_name in self._get_vrfs():
            conf_str = snippets.REMOVE_VRF % vrf_name
            self._edit_running_config(conf_str, 'REMOVE_VRF')

    def _do_remove_sub_interface(self, sub_interface):
        # optional: verify this is the correct sub_interface
        if self._interface_exists(sub_interface):
            conf_str = snippets.REMOVE_SUBINTERFACE % sub_interface
            self._edit_running_config(conf_str, 'REMOVE_SUBINTERFACE')

    def _get_config_by_regionid(self, regionid):
        """Get all config lines with the regionid."""
        ios_cfg = self._get_running_config()
        parse = HTParser(ios_cfg)
        regid_raw = parse.find_lines("^.*" + regionid)
        return regid_raw

    def remove_subinterface_by_regionid(self, regionid):
        subifs = self._get_regionid_subinterfaces(regionid)
        for intf in subifs:
            print "Removing subinterface {intf}".format(intf=intf)
            self._do_remove_sub_interface(intf)

    def remove_vrf_by_regionid(self, regionid):
        vrfs = self._get_vrfs()
        for vrf in vrfs:
            if regionid in vrf:
                print "Removing vrf config for {vrf}".format(vrf=vrf)
                self._do_remove_vrf(vrf)

    def remove_config_items_by_regionid(self, regionid):
        reg_cfg = self._get_config_by_regionid(regionid)
        num = 0
        for cfg in reg_cfg:
            num += 1
            print "Removing regionid config line #{num}: {cfg}".format(num=num,
                                                                       cfg=cfg)
            self._edit_running_config(CFG_LINE_SNIPPET % ("no " + cfg),
                                      regionid + "L" + str(num))


def cfgdata_to_iosxe_driver_cfg(cfg_data):
    xecfg_dev = []
    for rtr in cfg_data['routers']:
        print "Setting up Router {rtr}".format(rtr=rtr)
        if rtr in cfg_data['devices']:
            xecfg_dev.append(
                CfgIosXe(cfg_data['devices'][rtr]['ssh']['ipaddr'],
                         22,
                         cfg_data['devices'][rtr]['ssh']['user'],
                         cfg_data['devices'][rtr]['ssh']['password']))
    return xecfg_dev


def main():
    """ Get ASR config and cleanup ASR config for regionID"""
    LOG.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(
        description='Utility to clean CI configuration on ASR1K networking' +
        ' devices.')
    parser.add_argument('--config_file',
                        help='Path of configuration files describing'
                             ' devices\' connection info & networks.')
    parser.add_argument('--print_only',
                        default=False,
                        action='store_true',
                        help='Only print the current running configuration' +
                        ' data.')
    parser.add_argument('--regionID',
                        help='RegionID to print/delete config for.')

    args = parser.parse_args()

    with open(args.config_file, 'r') as cfgf:
        cfgfile_data = yaml.load(cfgf)

    devs = cfgdata_to_iosxe_driver_cfg(cfgfile_data)

    for dev in devs:
        intfs = dev._get_interfaces()
        print "Interfaces:"
        print intfs
        print "-------"

        vrfs = dev._get_vrfs()
        print "VRFs:"
        print vrfs
        print "-------"

        reg_intfs = dev._get_regionid_subinterfaces(args.regionID)
        print "Interfaces matching regionID:"
        print reg_intfs
        print "-------"

        region_cfg = dev._get_config_by_regionid(args.regionID)
        print "Region config:"
        print region_cfg
        print "-------"

        if not args.print_only:
            print "----------Removing stuff for regionID-----------"
            dev.remove_subinterface_by_regionid(args.regionID)
            dev.remove_vrf_by_regionid(args.regionID)

            print "remove config lines that are left with regionID:" + \
                "{reg}".format(reg=args.regionID)
            dev.update_running_config()
            dev.remove_config_items_by_regionid(args.regionID)
            print "----------End: Removing stuff for regionID-----------"


if __name__ == '__main__':
    main()
