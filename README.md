# Ansible-API
> ����ansible ģ��Ķ��ο���

> Ansible 2.4.1  
> Python 2.7

### AdHoc��
- init������ hosts, module, args����ز���
- run������ ���Դ���fork, gather_facts, inventory·�� �� ��������Ĭ��ֵ�����Բ��� ��������Ĭ��ֵ�����Բ���
- get_result�����������Զ��Ƶ�dict���������л���JSON����
- �ڷ���RESTfulЭ���ǰ��˷����ϵͳ�У�����AdHoc�࣬�������׶�������JSON��������Ӧ��JSON����
- �����ͼ
![uml_1](docs/img/uml_1.png)
### PlayBook��
- init: ���� hosts, playbook_path����ز���
- run���������Դ���fork, inventory·�� �� ��������Ĭ��ֵ�����Բ���
- get_result�����������Զ��Ƶ�dict���������л���JSON����
- �ڷ���RESTfulЭ���ǰ��˷����ϵͳ�У�����Playbook�࣬�������׶�������JSON��������Ӧ��JSON����
- - �����ͼ
![uml_2](docs/img/uml_2.png)