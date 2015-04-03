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
        self.processed_dependencies = []

    def get_role(self, role):
        for role in self.role_workbook:
            if role in role['groups']:
                return role
        return None

    def store_dependencies(self, task):
        if task is not None:
            for dependencie in task:
                if dependencie not in self.processed_dependencies:
                    self.dependencies.append(dependencie)

    def get_task(self, dependencie):
        for task in self.workbook:
            id = task.get('id', None)
            if id is not None and id == dependencie:
                self._data[id] = {
                    'puppet_modules': task.get('parameters', None).get('puppet_modules', None),
                    'puppet_manifest': task.get('parameters', None).get('puppet_manifest', None),
                }
                self.store_dependencies(task.get('requires', None))
                self.processed_dependencies.append(id)

    def get_data(self, role):
        role = self.get_role(role)
        if role is not None:
            id = role.get('id', None)
            if id is not None:
                self._data[id] = {
                    'puppet_modules': role.get('parameters', None).get('puppet_modules', None),
                    'puppet_manifest': role.get('parameters', None).get('puppet_manifest', None),
                }
                self.store_dependencies(role.get('requires', None))
                for dependencie in self.dependencies:
                    self.get_task(dependencie)
            else:
                print 'ID is not found!'
        else:
            print 'Role has not been found. Aborting.'

        return self._data

    def build_sequence(self, role):
        self.get_data(role)
        for id, puppet_properties in self.data.iteritems():
            print puppet_properties.get('puppet_modules', None), puppet_properties.get('puppet_manifest', None),

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
