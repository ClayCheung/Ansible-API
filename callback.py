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



class PlaybookCallBack(CallbackBase):
    def __init__(self, *args, **kwargs):
        super(PlaybookCallBack, self).__init__(*args, **kwargs)
        self.task_ok = {}
        self.task_failed = {}
        self.task_unreachable = {}
        self.task_skipped = {}
        self.task_status = {}

    def v2_runner_on_ok(self, result, *args, **kwargs):
        self.task_ok[result._host.get_name()] = result._result

    def v2_runner_on_failed(self, result, *args, **kwargs):
        self.task_failed[result._host.get_name()] = result._result

    def v2_runner_on_unreachable(self, result):
        self.task_unreachable[result._host.get_name()] = result._result

    def v2_runner_on_skipped(self, result):
        self.task_ok[result._host.get_name()] = result

    def v2_playbook_on_stats(self, stats):
        hosts = sorted(stats.processed.keys())
        for h in hosts:
            t = stats.summarize(h)
            self.task_status[h] = {
                "ok": t['ok'],
                "changed": t['changed'],
                "unreachable": t['unreachable'],
                "skipped": t['skipped'],
                "failed": t['failures']
            }