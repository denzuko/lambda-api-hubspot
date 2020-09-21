import hashlab
import string
import random

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature

from sqlalchemy.orm import validates
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Contact(Base):
    __tablename__ = 'contacts'

    email = Column(String, primary_key=True)
    id = Column(String)
