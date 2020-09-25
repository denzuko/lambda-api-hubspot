#!/usr/bin/which python3
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from celery import Celery, current_task, Task

@celery.task
def helloWorld():
    import time
    time.sleep(20)
    currentID = current_task.request.id
    return "hello world from {}".format(currentID)
