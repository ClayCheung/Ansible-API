#! /usr/bin/env python2
# -*- coding: utf-8 -*-
# __author__ = "ClayZhang"
# Date: 2019/5/5
import os

from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager

from callback import AdhocCallBack


class AdHoc(object):
    """
    input:
        - host
        - module
        - args
    output:
        - a dict of ad-hoc result
        {'success': {}, 'failed': {}, 'unreachable': {}}
    """
    def __init__(self, hosts, module, args):
        self.hosts = hosts
        self.module = module
        self.args = args
        self.options = None


    def check_cfg_and_inventory_exist(self, ansible_cfg_filePath, inventory_filePath):
        if not os.path.exists(ansible_cfg_filePath):
            raise ValueError('请先设置ansible.cfg配置文件\n默认路径：/home/ec2-user/workspace/script/ansible_v2_python2/ansible/ansible.cfg')
        if not os.path.exists(inventory_filePath):
            raise ValueError('请先设置inventory文件\n默认路径：/home/ec2-user/workspace/script/ansible_v2_python2/ansible/inventory/hosts')
        os.environ['ANSIBLE_CONFIG'] = ansible_cfg_filePath
        os.environ['ANSIBLE_HOST_KEY_CHECKING'] = 'False'

    def setOptions(self, fork):
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
        self.options = Options(connection='smart',
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

    def run(self, fork=5,
            gather_facts='no',
            ansible_cfg_filePath='/home/ec2-user/workspace/script/ansible_v2_python2/ansible/ansible.cfg',
            inventory_filePath='/home/ec2-user/workspace/script/ansible_v2_python2/ansible/inventory/hosts'):
        # 检查配置文件、检查inventory文件是否存在
        self.check_cfg_and_inventory_exist(ansible_cfg_filePath, inventory_filePath)

        #

        # 实例化一个YAML数据加载解析类实例
        loader = DataLoader()

        # 生成一个InventoryManager类 实例
        # 传参 loader：传入数据加载的实例
        # 传参 sources：传入一个列表，列表元素为文件系统中inventory的路径（绝对路径、相对路径均可），
        # 有多个inventory 则传入多个元素

        inventory = InventoryManager(loader=loader, sources=[inventory_filePath])

        # 实例化 VariableManager
        variableManager = VariableManager(loader=loader, inventory=inventory)
        # 通过方法或者成员变量，传入ansible变量
        # TODO 增加ansible变量，把这个作为可选参数传入
        # variableManager.get_vars()
        # variableManager.extra_vars =
        # variableManager.set_host_variable()

        # Set Options
        self.setOptions(fork)

        # 实例化Play()
        ## 指定ad-hoc操作内容：模块、参数
        play_operate = dict(
            name="Ansible Play ad-hoc of " + self.hosts,
            # 指定inventory中执行任务的主机范围
            hosts=self.hosts,
            gather_facts=gather_facts,
            tasks=[
                dict(
                    action=dict(
                        module=self.module,
                        args=self.args
                    )
                )
            ]

        )
        ## 实例化Play()
        play = Play().load(data=play_operate, variable_manager=variableManager, loader=loader)

        # 实例化TaskQueueManager，执行ad-hoc任务
        ## 重写 callback
        callback = AdhocCallBack()

        tqm = TaskQueueManager(inventory=inventory,
                               variable_manager=variableManager,
                               loader=loader,
                               options=self.options,
                               passwords=dict(),
                               stdout_callback=callback)
        tqm.run(play=play)

        # 自定制 返回的dict格式
        result_dict = {'success': {}, 'failed': {}, 'unreachable': {}}

        for host, res in callback.host_ok.items():
            result_dict['success'][host] = res
        for host, res in callback.host_failed.items():
            result_dict['failed'][host] = res
        for host, res in callback.host_unreachable.items():
            result_dict['unreachable'][host] = res

        return result_dict

if __name__ == '__main__':
    adhoc = AdHoc(hosts='test-group', module='shell', args='touch /tmp/ad-hoc_testClass_haha')
    result = adhoc.run()
    print type(result)
    print result
    import json
    print json.dumps(result)
