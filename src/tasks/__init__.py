from celery import Celery, states, Task, current_task
from urllib.parse import quote

from ..app import Secret, Settings 

mq = Celery('tasks', broker=quote('sqs://{}:{}@'.format(
    Secret('AWS_ACCESS_KEY'),
    Secret('AWS_SECRET_KEY')))

mq.conf.update(Settings('CELERY_CONFIG'))
mq.autodiscover_tasks()

__all__ = ('mq',)
