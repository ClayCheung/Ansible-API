# Ansible-API
> ����ansible ģ��Ķ��ο���

> Ansible 2.4.1  
> Python 2.7

### AdHoc��
- init������ hosts, module, args����ز���
- ����ѡ��ͨ��setOptions()�����������ò���
- ����ѡ��ͨ���޸�adhoc.baseInventoryFilePath��ֵ������ָ������inventory�ļ���·��
- ����ѡ��ͨ��set_dynamic_inventory(resource)����Ӷ�̬inventory
     > ע�⣺���붯̬��ӵ�������ִ��������Ҫ��ʵ�������ʱ��ָ��hosts��ֵΪ��̬����������ƣ�����ͨ��adhoc.hosts����hosts��
- run������ ���Դ��� gather_facts �Ȳ���
- get_result�����������Զ��Ƶ�dict���������л���JSON����
- �ڷ���RESTfulЭ���ǰ��˷����ϵͳ�У�����AdHoc�࣬�������׶�������JSON��������Ӧ��JSON����
- �����ͼ
![uml_1](docs/img/uml_1.png)
### PlayBook��
- init: ���� playbook_path����ز���
- ����ѡ��ͨ��setOptions()�����������ò���
    > playbook.setOptions(forks=10)
- ����ѡ��ͨ��baseInventoryFilePath����inventory·��
    > playbook.baseInventoryFilePath = 'path/of/base/playbook.yml'
- ����ѡ��ͨ��set_dynamic_inventory(resource)����Ӷ�̬inventory��
    > ע�⣺���붯̬��ӵ�������ִ��playbook,Ҫ��ִ�е�playbook.yml�ļ���ָ��hosts������̬��ӵ��飨Ĭ��������default_group��
- ��̬�����嵥�Ĵ��Σ�resource����ʽ��
    ```
    ## resource�ĸ�ʽ��
        ### 1. ������һ��ֻ��������������Ϣ��list,Ԫ����dict,ÿ��dict����һ̨��������Ϣ
        # resource =[
        #             {"hostname":"Nginx01","ip": "192.168.1.100", "port": "22", "username": "root", "password":"123456"},
        #             {"hostname":"Nginx02","ip": "192.168.1.101", "port": "22", "username": "root", "password":"123456"},
        #           ]
        #
        ### 2. ������һ��ֻ���������顢����������Ϣ��������Ϣ��dict
        resource = {
            "dynamic-group01": {
                "hosts": [
                    {"hostname": "Nginx01", "ip": "192.168.1.100", "port": "22", "username": "root", "password": "123456"},
                    {"hostname": "Nginx02", "ip": "192.168.1.101", "port": "22", "username": "root", "password": "123456"},
                ],
                "vars": {
                    "var1": "dynamic_inventory",
                    "var2": "resource�ĸ�ʽ��key���ܱ䣬����Ϊ��"
                }
            }
        }
    ```
- run������ִ��playbook 
- get_result�����������Զ��Ƶ�dict���������л���JSON����
- �ڷ���RESTfulЭ���ǰ��˷����ϵͳ�У�����Playbook�࣬�������׶�������JSON��������Ӧ��JSON����
- - �����ͼ
![uml_2](docs/img/uml_2.png)

# ��ʼ����ʵ����Playbook�ࣺ�ɴ��� hosts, playbook_path��Щ����
    playbook = Playbook(playbook_path_list=['/home/ec2-user/workspace/script/ansible_v2_python2/ansible/playbook/playbook.yml'])
    # ����ѡ��ͨ��setOptions()�����������ò���
    playbook.setOptions(forks=10)
    # ����ѡ��ͨ��baseInventoryFilePath����inventory·��
    # playbook.baseInventoryFilePath = 'path/of/base/playbook.yml'
    # ����ѡ��ͨ��set_dynamic_inventory(resource)����Ӷ�̬inventory��
    # ע�⣺���붯̬��ӵ�������ִ��playbook,Ҫ��ִ�е�playbook.yml�ļ���ָ��hosts������̬��ӵ��飨Ĭ��������default_group��
    ## resource�ĸ�ʽ��
    ### 1. ������һ��ֻ��������������Ϣ��list,Ԫ����dict,ÿ��dict����һ̨��������Ϣ
    # resource =[
    #             {"hostname":"Nginx01","ip": "192.168.1.108", "port": "22", "username": "root", "password":"123456"},
    #             {"hostname":"Nginx02","ip": "192.168.1.109", "port": "22", "username": "root", "password":"123456"},
    #           ]
    #
    ### 2. ������һ��ֻ���������顢����������Ϣ��������Ϣ��dict
    resource = {
        "dynamic-group01": {
            "hosts": [
                {"hostname": "Nginx01", "ip": "192.168.1.108", "port": "22", "username": "root", "password": "123456"},
                {"hostname": "Nginx02", "ip": "192.168.1.109", "port": "22", "username": "root", "password": "123456"},
            ],
            "vars": {
                "var1": "dynamic_inventory",
                "var2": "resource�ĸ�ʽ��key���ܱ䣬����Ϊ��"
            }
        }
    }

    playbook.set_dynamic_inventory(resource)
    # run����ִ��playbook
    ## playbook��ִ��hosts��Χ����playbook.yml�ļ����趨�����Զ�ָ̬��playbook�ļ�
    ## Ĭ�ϵ�playbook�ļ���hostsû��ָ��"dynamic-group01"����飬��������ָ����dynamic inventoryʵ���ϲ��ᱻ����ִ�з�Χ