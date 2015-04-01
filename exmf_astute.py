#!/usr/bin/env python

import operator
import yaml
import shlex
import sys

from subprocess import Popen, PIPE

yaml_file='/etc/astute.yaml'
puppet_debug_opt='-d -v -l /tmp/test.log'
puppet_tags_opt='--tags=nova_config,nova_paste_api_ini,neutron_config,neutron_api_config,neutron_dhcp_agent_config,neutron_fwaas_service_config,neutron_l3_agent_config,neutron_lbaas_agent_config,neutron_metadata_agent_config,neutron_metering_agent_config,neutron_plugin_cisco,neutron_plugin_cisco_credentials,neutron_plugin_cisco_db_conn,neutron_plugin_cisco_l2network,neutron_plugin_linuxbridge,neutron_plugin_ml2,neutron_plugin_nvp,neutron_plugin_ovs,neutron_vpnaas_agent_config'


with open(yaml_file, 'r') as opened_yaml_file:
    try:
        astute_dic=yaml.safe_load(opened_yaml_file)
    except ScannerError:
        print "Wrong .yaml file format, please check the content"
        sys.exit(2)

if len(astute_dic['tasks']) > 0:
    sorted_tasks_by_priority = sorted(astute_dic['tasks'], key=lambda k: k['priority'])
    for i in sorted_tasks_by_priority:
        try:
            puppet_modules = i['parameters']['puppet_modules']
            puppet_manifest = i['parameters']['puppet_manifest']
        except:
            continue

        print puppet_modules
        print puppet_manifest

        puppet_cmd = 'puppet apply %s %s --modulepath=%s %s' % (puppet_debug_opt, puppet_tags_opt, puppet_modules, puppet_manifest)
        
        process = Popen(shlex.split(puppet_cmd), stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
