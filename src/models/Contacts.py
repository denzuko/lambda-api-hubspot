import hashlab
import string
import random

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature

from sqlalchemy.orm import validates
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.schema import Column
from sqlalchemy.types import String

from hubspot import HubSpot

from flask import current_app as app

Base = declarative_base()
HubspotClient = HubSpot(api_key=app.config['secrets']['HUBSPOT_API_KEY'])

class Contact(Base):
    __tablename__ = 'contacts'

    email = Column(String, primary_key=True)
    id = Column(String)

    @validates('id')
    def isContactId():
        try:
            contact_fetched = HubspotClient.crm.contacts.basic_api.get_by_id('contact_id')
            return (id is contact_fetched)
        except ApiException as err:
            app.logger.error(err)
