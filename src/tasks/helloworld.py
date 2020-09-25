#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from celery import Celery, current_task, Task

from . import mq

@mq.task
def helloWorld():
    import time
    time.sleep(20)
    currentID = current_task.request.id
    return "hello world from {}".format(currentID)
