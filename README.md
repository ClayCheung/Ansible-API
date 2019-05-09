# Ansible-API
> 基于ansible 模块的二次开发

> Ansible 2.4.1  
> Python 2.7

### AdHoc类
- init：传入 hosts, module, args等相关参数
- （可选）通过setOptions()方法重新设置参数
- （可选）通过修改adhoc.baseInventoryFilePath的值，重新指定基本inventory文件的路径
- （可选）通过set_dynamic_inventory(resource)：添加动态inventory
     > 注意：若想动态添加的主机被执行任务，需要在实例化类的时候指定hosts的值为动态主机组的名称（或者通过adhoc.hosts重置hosts）
- run方法： 可以传入 gather_facts 等参数
- get_result方法：返回自定制的dict，便于序列化成JSON数据
- 在符合RESTful协议的前后端分离的系统中，调用AdHoc类，即可容易定制请求JSON数据与响应的JSON数据
- 类调用图
![uml_1](docs/img/uml_1.png)
### PlayBook类
- init: 传入 playbook_path等相关参数
- （可选）通过setOptions()方法重新设置参数
    > playbook.setOptions(forks=10)
- （可选）通过baseInventoryFilePath设置inventory路劲
    > playbook.baseInventoryFilePath = 'path/of/base/playbook.yml'
- （可选）通过set_dynamic_inventory(resource)：添加动态inventory，
    > 注意：若想动态添加的主机被执行playbook,要在执行的playbook.yml文件中指定hosts包含动态添加的组（默认组名：default_group）
- 动态主机清单的传参（resource）格式：
    ```
    ## resource的格式：
        ### 1. 可以是一个只包含主机连接信息的list,元素是dict,每个dict包含一台主机的信息
        # resource =[
        #             {"hostname":"Nginx01","ip": "192.168.1.100", "port": "22", "username": "root", "password":"123456"},
        #             {"hostname":"Nginx02","ip": "192.168.1.101", "port": "22", "username": "root", "password":"123456"},
        #           ]
        #
        ### 2. 可以是一个只包含主机组、主机连接信息、变量信息的dict
        resource = {
            "dynamic-group01": {
                "hosts": [
                    {"hostname": "Nginx01", "ip": "192.168.1.100", "port": "22", "username": "root", "password": "123456"},
                    {"hostname": "Nginx02", "ip": "192.168.1.101", "port": "22", "username": "root", "password": "123456"},
                ],
                "vars": {
                    "var1": "dynamic_inventory",
                    "var2": "resource的格式：key不能变，可以为空"
                }
            }
        }
    ```
- run方法：执行playbook 
- get_result方法：返回自定制的dict，便于序列化成JSON数据
- 在符合RESTful协议的前后端分离的系统中，调用Playbook类，即可容易定制请求JSON数据与响应的JSON数据
- - 类调用图
![uml_2](docs/img/uml_2.png)

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