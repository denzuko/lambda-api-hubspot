from celery import Task
from sqlalchemy.orm.exc import NoResultFound
from flask import current_app as app

from ..models import Contact

class SqlTask(Task):
	"""
	abstract task that ensures the db connection is closed after execution
	"""
	abstract = True

	def after_return(self, status, retval, task_id, args, kwargs, einfo):
		app.data.driver.session.remove()

@celery.task(base=SqlTask, max_retries=10, default_retry_delay=60)
def get_contact_from_database(contact_id):
	try:
		user = app.data.driver.session(Contacts).Filter(Contact.id=contact_id).one()
		return user
	except NoResultFound as err:
		raise get_contact_from_database.retry(exc=err)

@celery.task(base=SqlTask, max_retries=10, default_retry_delay=60)
def add_contact():
    """
    todo: pull object from sqs
    """
    dbsession = app.data.driver.session
    logger    = app.logger

    try:
        dbsession.add(Contact(
            email="james.johnson@example.com"))
        dbsession.commit()
        dbsession.flush()
        return True
    except sqlalchemy.exc.SQLAlchemyError as err:
        logger.error(err.args)
        dbsession.rollback()
        return False
