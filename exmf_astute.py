#!/usr/bin/env python

import operator
import yaml
import shlex
import sys

from subprocess import Popen, PIPE

yaml_file='/etc/astute.yaml'
puppet_debug_opt='-d -v'
puppet_tags_opt='--tags=nova_config,nova_paste_api_ini'

try:
    opened_yaml_file = open(yaml_file, 'r')
except e:
    sys.exit(1)
try:
    astute_dic=yaml.safe_load(opened_yaml_file)
except ScannerError:
    print "Wrong file format, please check the content"
    sys.exit(2)

opened_yaml_file.close()

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
        
        print subprocess.Popen(shlex.split(puppet_cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
