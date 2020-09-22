from celery import Celery, current_task

@celery.task
def helloWorld():
    import time
    time.sleep(20)
    currentID = current_task.request.id
    return "hello world from {}".format(currentID)
