from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship, validates

from flask import current_app as app
from hubspot3 import HubSpot3 as HubSpot

from . import BaseModel

HubspotClient = HubSpot(api_key=app.config['secrets']['HUBSPOT_API_KEY'])

class Contact(BaseMixin, BaseModel):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    contact_id = Column(Integer)
    company_id = Column(Integer)
    email = Column(String(255))

    def __init__(self, email, crm_id):
        contact_fetched = HubSpotClient.contacts.get_contact_by_email(self.email)
        self.contact_id = contact_fetched['identity-profiles']['vid']

    def hasCrmEmail(self):
        contact_fetched = HubSpotClient.contacts.get_contact_by_email(self.email)
        return true if 'vid' in contact_fetched else false
        
    @validates('contact_id')
    def isContactId(self):
        contact_fetched = HubspotClient.contacts.get_contact_by_email(self.email)

        if len(contact_fetched['vid']) > 0):
            return (id is contact_fetched['vid'])

        return False
