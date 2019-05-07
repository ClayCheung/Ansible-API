#! /usr/bin/env python2
# -*- coding: utf-8 -*-
# __author__ = "ClayZhang"
# Date: 2019/5/7

from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager
from ansible.executor.playbook_executor import PlaybookExecutor

from callback import PlaybookCallBack



inventory_filePath = '/home/ec2-user/workspace/script/ansible_v2_python2/ansible/inventory/hosts'
playbook_filePath = '/home/ec2-user/workspace/script/ansible_v2_python2/ansible/playbook/playbook.yml'



# 实例化一个YAML数据加载解析类实例
loader = DataLoader()

# 生成一个InventoryManager类 实例
inventory = InventoryManager(loader=loader, sources=[inventory_filePath])

# 实例化 VariableManager
variableManager = VariableManager(loader=loader, inventory=inventory)
# 通过方法或者成员变量，传入ansible变量
# variableManager.get_vars()
# variableManager.extra_vars =
# variableManager.set_host_variable()

# namedtuple 返回一个类(有名字的tuple)
Options = namedtuple('Options', [
                                    'connection',
                                    'remote_user',
                                    'ask_sudo_pass',
                                    'verbosity',
                                    'ack_pass',
                                    'module_path',
                                    'forks',
                                    'become',
                                    'become_method',
                                    'become_user',
                                    'check',
                                    'listhosts',
                                    'listtasks',
                                    'listtags',
                                    'syntax',
                                    'sudo_user',
                                    'sudo',
                                    'diff'
                                ])
# 设置options
options = Options(connection='smart',
                  remote_user=None,
                ask_sudo_pass=False,
                verbosity=5,
                ack_pass=False,
                module_path=None,
                forks=5,
                become=None,
                become_method=None,
                become_user=None,
                check=False,
                listhosts=None,
                listtasks=None,
                listtags=None,
                syntax=None,
                sudo_user=None,
                sudo=None,
                diff=False
                )

playbook = PlaybookExecutor(playbooks=[playbook_filePath,],
                            inventory=inventory,
                            variable_manager=variableManager,
                            loader=loader,
                            options=options,
                            passwords=dict())

callback = PlaybookCallBack()
playbook._tqm._stdout_callback = callback
playbook.run()

result_dict = {"status":{}, 'success':{}, 'failed':{}, 'unreachable':{}, "changed":{}, 'skipped':{}}
for host, result in callback.task_ok.items():
    result_dict['success'][host] = result

for host, result in callback.task_failed.items():
    result_dict['failed'][host] = result

for host, result in callback.task_status.items():
    result_dict['status'][host] = result

# for host, result in self.callback.task_changed.items():
#     self.results_raw['changed'][host] = result

for host, result in callback.task_skipped.items():
    result_dict['skipped'][host] = result

for host, result in callback.task_unreachable.items():
    result_dict['unreachable'][host] = result
print result_dict