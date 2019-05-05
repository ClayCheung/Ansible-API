#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = "ClayZhang"
# Date: 2019/5/5

from ansible.executor.task_queue_manager import CallbackBase

class AdhocCallBack(CallbackBase):
    def __init__(self, *args, **kwargs):
        super(AdhocCallBack, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_failed = {}
        self.host_unreachable = {}


    def v2_runner_on_failed(self, result, *args, **kwargs):
        host = result._host.get_name()
        self.host_failed[host] = result._result

    def v2_runner_on_ok(self, result, *args, **kwargs):
        host = result._host.get_name()
        self.host_ok[host] = result._result

    def v2_runner_on_unreachable(self, result, *args, **kwargs):
        host = result._host.get_name()
        self.host_unreachable[host] = result._result