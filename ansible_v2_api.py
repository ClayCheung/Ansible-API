#! /usr/bin/env python2
# -*- coding: utf-8 -*-
# __author__ = "ClayZhang"
# Date: 2019/5/5
import os
from collections import namedtuple

from ansible import constants
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.inventory.host import Host, Group
from ansible.vars.manager import VariableManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.executor.playbook_executor import PlaybookExecutor

from callback import AdhocCallBack, PlaybookCallBack


class AnsibleBase(object):
    """
    Ansible基类
    """

    def __init__(self):
        self.options = None
        self.callback = None

        self.loader = None
        self.inventory = None
        self.variableManager = None
        self.resource = None
        self.password = dict(sshpass=None, becomepass=None)
        self.baseInventoryFilePath = '/home/ec2-user/workspace/script/ansible_v2_python2/ansible/inventory/hosts'
        self.ansible_cfg_filePath = '/home/ec2-user/workspace/script/ansible_v2_python2/ansible/ansible.cfg'

        self.__initializeData()

    def __initializeData(self):
        """
        设置最初的默认数据（默认inventory, 默认variable, 默认loader, 默认options）
        :return:
        """

        self.loader = DataLoader()

        # 生成一个InventoryManager类 实例
        # 传参 loader：传入数据加载的实例
        # 传参 sources：传入一个列表，列表元素为文件系统中inventory的路径（绝对路径、相对路径均可），
        # 有多个inventory 则传入多个元素

        self.inventory = InventoryManager(loader=self.loader, sources=[self.baseInventoryFilePath])

        # 实例化 VariableManager
        self.variableManager = VariableManager(loader=self.loader, inventory=self.inventory)
        # 按默认值设置options,如果需要自定义option，可以实例化后再次调用setOptions()方法
        self.setOptions()

    def setOptions(self, connection='smart',
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
                          diff=False):
        """
        调用此方法可以重置连接参数
        """
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
        self.options = Options(connection=connection,
                          remote_user=remote_user,
                          ask_sudo_pass=ask_sudo_pass,
                          verbosity=verbosity,
                          ack_pass=ack_pass,
                          module_path=module_path,
                          forks=forks,
                          become=become,
                          become_method=become_method,
                          become_user=become_user,
                          check=check,
                          listhosts=listhosts,
                          listtasks=listtasks,
                          listtags=listtags,
                          syntax=syntax,
                          sudo_user=sudo_user,
                          sudo=sudo,
                          diff=diff
                          )

    def add_dynamic_group(self, hosts_list, groupname, groupvars=None):
        """
            add group
        """
        self.inventory.add_group(groupname)
        my_group = Group(name=groupname)

        # if group variables exists, add them to group
        if groupvars:
            for key, value in groupvars.iteritems():    # iteritems()返回的是迭代器，items()返回的是列表
                my_group.set_variable(key, value)

        # add hosts to group
        for host in hosts_list:
            # set connection variables
            hostname = host.get("hostname")
            hostip = host.get('ip', hostname)
            hostport = host.get("port")
            username = host.get("username")
            password = host.get("password")
            # 如果不存在，默认值是None
            ssh_key = host.get("ssh_key")
            my_host = Host(name=hostname, port=hostport)
            self.variableManager.set_host_variable(host=my_host, varname='ansible_ssh_host', value=hostip)
            self.variableManager.set_host_variable(host=my_host, varname='ansible_ssh_pass', value=password)
            self.variableManager.set_host_variable(host=my_host, varname='ansible_ssh_port', value=hostport)
            self.variableManager.set_host_variable(host=my_host, varname='ansible_ssh_user', value=username)
            self.variableManager.set_host_variable(host=my_host, varname='ansible_ssh_private_key_file', value=ssh_key)
            # my_host.set_variable('ansible_ssh_pass', password)
            # my_host.set_variable('ansible_ssh_private_key_file', ssh_key)

            # set other variables
            for key, value in host.iteritems():
                if key not in ["hostname", "port", "username", "password"]:
                    self.variableManager.set_host_variable(host=my_host, varname=key, value=value)

            # add to group
            self.inventory.add_host(host=hostname, group=groupname, port=hostport)

    def set_dynamic_inventory(self, resource):
        self.resource = resource
        # 如果要在指定组（新建组）里添加新主机，并添加变量（可选）
        if type(resource) == dict:
            for groupname, hosts_and_vars in self.resource.iteritems():
                self.add_dynamic_group(hosts_list = hosts_and_vars.get("hosts"),
                                       groupname = groupname,
                                       groupvars = hosts_and_vars.get("vars"))
        # 如果只在默认组里添加主机的登录方式，不带变量
        elif isinstance(self.resource, list):
            self.add_dynamic_group(hosts_list = self.resource, groupname = 'default_group')


    def run(self, *args, **kwargs):
        """
        需要被重写
        """
        pass

    def get_result(self, *args, **kwargs):
        """
        需要被重写, 自定义callback
        """
        pass








class AdHoc(AnsibleBase):
    """
    input:
        - hosts
        - module
        - args
    output:
        - a dict of ad-hoc result
        {'success': {}, 'failed': {}, 'unreachable': {}}
    """
    def __init__(self, hosts, module, module_args):
        super(AdHoc, self).__init__()
        self.hosts = hosts
        self.module = module
        self.module_args = module_args


    # TODO 增加动态inventory导入方法

    def check_cfg_and_inventory_exist(self, ansible_cfg_filePath, inventory_filePath):
        if not os.path.exists(ansible_cfg_filePath):
            raise ValueError('ansible_config文件不存在： %s\n' % ansible_cfg_filePath)

        if not os.path.exists(inventory_filePath):
            raise ValueError('inventory文件不存在： %s\n' % inventory_filePath)
        # 关闭第一次使用ansible连接客户端时输入命令，相当于配置环境变量
        constants.HOST_KEY_CHECKING = False
        os.environ['ANSIBLE_CONFIG'] = ansible_cfg_filePath
        # os.environ['ANSIBLE_HOST_KEY_CHECKING'] = 'False'



    def run(self, gather_facts='no'):
        # 检查配置文件、检查inventory文件是否存在
        self.check_cfg_and_inventory_exist(self.ansible_cfg_filePath, self.baseInventoryFilePath)

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
                        args=self.module_args
                    )
                )
            ]

        )
        ## 实例化Play()
        play = Play().load(data=play_operate, variable_manager=self.variableManager, loader=self.loader)

        # 实例化TaskQueueManager，执行ad-hoc任务
        ## 重写 callback
        self.callback = AdhocCallBack()

        tqm = TaskQueueManager(inventory=self.inventory,
                               variable_manager=self.variableManager,
                               loader=self.loader,
                               options=self.options,
                               passwords=self.password,
                               stdout_callback=self.callback)
        tqm.run(play=play)

        # 返回True 表示ansible任务已经执行，可用于判断
        return True


    def get_result(self):
        # 自定制 返回的dict格式
        result_dict = {'success': {}, 'failed': {}, 'unreachable': {}}

        for host, res in self.callback.host_ok.items():
            result_dict['success'][host] = res
        for host, res in self.callback.host_failed.items():
            result_dict['failed'][host] = res
        for host, res in self.callback.host_unreachable.items():
            result_dict['unreachable'][host] = res

        return result_dict


class Playbook(AnsibleBase):
    """
    input:
        - hosts
        - playbook.yml文件

    output:
        - a dict of playbook result
        {"status":{}, 'success':{}, 'failed':{}, 'unreachable':{}, "changed":{}, 'skipped':{}}
    """
    playbook_defaultFilePath = '/home/ec2-user/workspace/script/ansible_v2_python2/ansible/playbook/playbook.yml'
    def __init__(self, playbook_path_list):
        super(Playbook, self).__init__()

        # 如果没传入playbook路径，则使用默认路径
        if  playbook_path_list == None:
            self.playbook_path_list = ['/home/ec2-user/workspace/script/ansible_v2_python2/ansible/playbook/playbook.yml']
        else: # 如果传入playbook路径
            self.playbook_path_list = playbook_path_list



    def check_cfg_and_inventory_exist(self, ansible_cfg_filePath, inventory_filePath, playbook_path_list):
        if not os.path.exists(ansible_cfg_filePath):
            raise ValueError('ansible_config文件不存在： %s\n'%ansible_cfg_filePath)

        if not os.path.exists(inventory_filePath):
            raise ValueError('inventory文件不存在： %s\n'%inventory_filePath)

        for playbook_path in playbook_path_list:
            if not os.path.exists(playbook_path):
                raise ValueError('playbook文件不存在： %s\n'%playbook_path)

        # 关闭第一次使用ansible连接客户端时输入命令，相当于配置环境变量
        constants.HOST_KEY_CHECKING = False
        os.environ['ANSIBLE_CONFIG'] = ansible_cfg_filePath
        # os.environ['ANSIBLE_HOST_KEY_CHECKING'] = 'False'



    # TODO 把指定ansible.cfg 指定inventory，这些参数的传入写到一个新的方法中（set_cfg_and_inventory）,

    def run(self):
        # 检查配置文件、检查inventory文件是否存在
        self.check_cfg_and_inventory_exist(self.ansible_cfg_filePath, self.baseInventoryFilePath, self.playbook_path_list)


        # 通过方法或者成员变量，传入ansible变量
        # variableManager.get_vars()
        # variableManager.extra_vars =
        # variableManager.set_host_variable()


        # 实例化PlaybookExecutor()
        playbook = PlaybookExecutor(playbooks=self.playbook_path_list,
                                    inventory=self.inventory,
                                    variable_manager=self.variableManager,
                                    loader=self.loader,
                                    options=self.options,
                                    passwords=dict())

        ## 重写 callback
        self.callback = PlaybookCallBack()
        playbook._tqm._stdout_callback = self.callback
        ## 执行playbook
        playbook.run()

        # 返回True 表示ansible-playbook已经执行，可用于判断
        return True


    def get_result(self):
        # 自定制 返回的dict格式
        result_dict = {"status": {}, 'success': {}, 'failed': {}, 'unreachable': {}, "changed": {}, 'skipped': {}}

        for host, result in self.callback.task_ok.items():
            result_dict['success'][host] = result

        for host, result in self.callback.task_failed.items():
            result_dict['failed'][host] = result

        for host, result in self.callback.task_status.items():
            result_dict['status'][host] = result

        # for host, result in self.callback.task_changed.items():
        #     self.results_raw['changed'][host] = result

        for host, result in self.callback.task_skipped.items():
            result_dict['skipped'][host] = result

        for host, result in self.callback.task_unreachable.items():
            result_dict['unreachable'][host] = result

        return result_dict


if __name__ == '__main__':
    print '----- Ad-Hoc-Test -----'
    # 初始化、实例化AdHoc类：hosts, module, args 是必填参数
    adhoc = AdHoc(hosts='test-group', module='shell', module_args='touch /tmp/ad-hoc_testClass_haha')
    # （可选）通过setOptions()方法重新设置参数
    adhoc.setOptions(forks=10)
    # （可选）通过修改adhoc.baseInventoryFilePath的值，重新指定基本inventory文件的路径
    # （可选）通过set_dynamic_inventory(resource)：添加动态inventory，
    #  注意：若想动态添加的主机被执行任务，需要在实例化类的时候指定hosts的值为动态主机组的名称（或者通过adhoc.hosts重置hosts）
    # run方法可以传入 gather_facts 参数，有默认值，可以不传
    isExecute = adhoc.run(gather_facts='no')
    print 'isExecute: '+str(isExecute)
    import json
    print json.dumps(adhoc.get_result())




    print '----- Playbook-Test -----'
    # 初始化、实例化Playbook类：可传入 hosts, playbook_path这些参数
    playbook = Playbook(playbook_path_list=['/home/ec2-user/workspace/script/ansible_v2_python2/ansible/playbook/playbook.yml'])
    # （可选）通过setOptions()方法重新设置参数
    playbook.setOptions(forks=10)
    # （可选）通过baseInventoryFilePath设置inventory路劲
    # playbook.baseInventoryFilePath = 'path/of/base/playbook.yml'
    # （可选）通过set_dynamic_inventory(resource)：添加动态inventory，
    # 注意：若想动态添加的主机被执行playbook,要在执行的playbook.yml文件中指定hosts包含动态添加的组（默认组名：default_group）
    ## resource的格式：
    ### 1. 可以是一个只包含主机连接信息的list,元素是dict,每个dict包含一台主机的信息
    # resource =[
    #             {"hostname":"Nginx01","ip": "192.168.1.108", "port": "22", "username": "root", "password":"123456"},
    #             {"hostname":"Nginx02","ip": "192.168.1.109", "port": "22", "username": "root", "password":"123456"},
    #           ]
    #
    ### 2. 可以是一个只包含主机组、主机连接信息、变量信息的dict
    resource = {
        "dynamic-group01": {
            "hosts": [
                {"hostname": "Nginx01", "ip": "192.168.1.108", "port": "22", "username": "root", "password": "123456"},
                {"hostname": "Nginx02", "ip": "192.168.1.109", "port": "22", "username": "root", "password": "123456"},
            ],
            "vars": {
                "var1": "dynamic_inventory",
                "var2": "resource的格式：key不能变，可以为空"
            }
        }
    }

    playbook.set_dynamic_inventory(resource)
    # run方法执行playbook
    ## playbook的执行hosts范围，在playbook.yml文件中设定，可以动态指定playbook文件
    ## 默认的playbook文件中hosts没有指定"dynamic-group01"这个组，所以上面指定的dynamic inventory实际上不会被加入执行范围
    isPlaybookExecute = playbook.run()
    if isPlaybookExecute:
        import json
        print json.dumps(playbook.get_result())
