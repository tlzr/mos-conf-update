#!/usr/bin/env python

import argparse
import os
import yaml
import sys

class MakeTree:
    def __init__(self):
        self._data = {}
        self.workbook = []
        self.role_workbook = []
        self.dependencies = []
        self.id_n = 0

    def get_role(self, role):
        for group in self.role_workbook:
            type = group.get('type', None)
            if role in group['groups'] and type == 'puppet':
                return group
        return None

    def store_dependencies(self, task):
        requirements = task.get('requires', None)
        if requirements is not None:
            for dependencie in requirements:
                if dependencie not in self.dependencies:
                    self.dependencies.append(dependencie)

    def get_task(self, dependencie):
        for task in self.workbook:
            id = task.get('id', None)
            parameters = task.get('parameters', None)
            if id is not None and id == dependencie and parameters is not None:
                self.fill_data(task)
                self.store_dependencies(task)

    def get_data(self, role):
        role = self.get_role(role)
        if role is not None:
            id = role.get('id', None)
            if id is not None:
                self.fill_data(role)
                self.store_dependencies(role)
                for dependencie in self.dependencies:
                    self.get_task(dependencie)
            else:
                print 'ID is not found!'
        else:
            print 'Role has not been found. Aborting.'
            sys.exit(1)

    def fill_data(self, data):
        id = data.get('id', None)
        self._data[self.id_n] = {
            'id': id,
            'puppet_modules': data.get('parameters', None).get('puppet_modules', None),
            'puppet_manifest': data.get('parameters', None).get('puppet_manifest', None),
        }
        self.id_n += 1

    def build_sequence(self, role):
        self.get_data(role)
        self._data = sorted(self._data.items(), key=lambda k: k[0], reverse=True)
        for id, puppet_properties in self.data:
            print puppet_properties.get('puppet_modules', None)
            print puppet_properties.get('puppet_manifest', None)

    def load_yaml(self, yaml_workbook):
        self.workbook = yaml.load(yaml_workbook)

    def load_role_yaml(self, yaml_workbook):
        self.role_workbook = yaml.load(yaml_workbook)

    @property
    def data(self):
        return self._data

def make_sequence(yaml_tasks, role):
    DEPLOYMENT_CURRENT = ""
    ROLE_TASK = ""
    for root, dirs, files in os.walk(yaml_tasks):
        for file in files:
            if file.endswith('tasks.yaml'):
                full_path = os.path.join(root, file)
                #print("\t%s" % full_path)
                with open(full_path, "r") as yamlfile:
                    if full_path.endswith('roles/tasks.yaml'):
                        ROLE_TASK = yamlfile.read()
                    else:
                        DEPLOYMENT_CURRENT += yamlfile.read()

    mf = MakeTree()
    mf.load_role_yaml(ROLE_TASK)
    mf.load_yaml(DEPLOYMENT_CURRENT)
    mf.build_sequence(role)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get deploy tasks by role.')
    parser.add_argument("tasks_directory", type=str, help="Directory with Fuel tasks.yaml files", default='./osnailyfacter/modular')
    parser.add_argument("-r", "--role", help="Role, e.g. 'ceph-osd'", default='primary-controller')
    args = parser.parse_args()

    make_sequence(args.tasks_directory, args.role)
