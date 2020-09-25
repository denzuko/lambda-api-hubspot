#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from eve_sqlalchemy.config import DomainConfig, ResourceConfig

from flask import current_app as instance

from . import Contacts

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    _created = Column(DateTime, default=func.now())
    _updated = Column(DateTime, default=func.now(), onupdate=func.now())
    _etag = Column(String(40))

class BaseMixin(object):
    @classmethod
    def create(cls, **kw):
        obj = cls(**kw)

        instance.data.driver.session.add(obj)
        instance.data.driver.session.commit()

def Domain():
    return DomainConfig(dict(
        contacts=ResourceConfig(Contacts)))

__all__ = (Domain, Contacts, )
