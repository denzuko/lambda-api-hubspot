from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates

from hubspot3 import HubSpot3 as HubSpot

from flask import current_app as app

from . import BaseModel

HubspotClient = HubSpot(api_key=app.config['secrets']['HUBSPOT_API_KEY'])

class Contact(BaseModel):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    crm_id = Column(String(255))
    email = Column(String(255))

    @validates('crm_id')
    def isContactId():
        try:
            contact_fetched = HubspotClient.contacts.get_contact_by_email(self.email)
            return (id is contact_fetched['vid'])
        except ApiException as err:
            app.logger.error(err)

    @classmethod
    def create(cls, **kw):
        obj = cls(**kw)

        self.crm_id = HubSpotClient.contacts.get_contact_by_email(self.email)

        db.session.add(obj)
        db.session.commit()

