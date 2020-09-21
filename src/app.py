#!/usr/bin/which python3
import os
import base64
import logging

import boto3
import boto3.exceptions
import botocore.exceptions

from cloudwatch import CloudwatchHandler

from .models import Contacts

from eve import Eve
from eve_swagger import get_swagger_blueprint, add_documentation
from eve_healthcheck import EveHealthCheck
from eve_sqlalchemy.validation import ValidatorSQL
from eve_sqlalchemy import SQL
from sqlalchemy.ext.declaritive import declaritive_base

from flask import current_app

def Domain():
    return {
        'contact': {
            'item_title': 'contact',
            'description': 'Creates a contact record',
            'schema': { 
                'fullName':  dict(type=str(),minlength=1,maxlength=256,required=True),
                'email': dict(type=str(), minlength=4,maxlength=512,required=True)
            }
        }
    }

def OpenApi():  
    return  {
        'title': os.getenv('AWS_LAMBDA_FUNCTION_NAME',__file__),
        'version': '1.0',
        'description': '',
        'termsOfService': '',
        'contact': {
            'name': 'Dwight Spencer',
            'url': 'https://dwightaspencer.com/'
        },
        'license': {
            'name': 'BSD',
            'url': 'https://opensource.org/licenses/BSD-2-Clause'
        },
        'schemes': ['http', 'https']
    }

def Settings(key):
    settings = {
            'X_DOMAINS': ['*'],
            'X_HEADERS': ['Origin', 'X-Requested-With', 'Content-Type', 'If-Match', 'Authorization'],
            'RENDERERS': ['eve.render.JSONRenderer'],
            'JSON_SORT_KEYS': True,
            'JSONP_ARGUMENT': 'callback',
            'SCHEMA_ENDPOINT ': '/schema',
            'SWAGGER_INFO':  OpenApi(),
            'SWAGGER_EXAMPLE_FIELD_REMOVE': True,
            'TRANSPARENT_SCHEMA_RULES': True,
            'X_ALLOW_CREDENTIALS': True,
            'ITEM_METHODS': ['GET', 'PATCH', 'DELETE'],
            'RESOURCE_METHODS': ['GET'],
            'DOMAIN': Domain(),
            'secrets': {
                'AWS_KEY_ID': os.getenv('AWS_KEY_ID',''),
                'AWS_SECRET_KEY': os.getenv('AWS_SECRET_KEY',''),
                'AWS_REGION': os.getenv('AWS_REGION',''),
                'AWS_LOG_GROUP': os.getenv('AWS_LOG_GROUP',''),
                'AWS_LOG_STREAM': os.getenv('AWS_LOG_STREAM','')
            }
    }

    return settings.get(key, settings)

def Logger():
    logger = logging.getLogger(Settings('SWAGGER_INFO')['title'])
    logger.addHandler(CloudwatchHandler(
        Settings('secrets')['AWS_KEY_ID'],
        Settings('secrets')['AWS_SECRET_KEY'],
        Settings('secrets')['AWS_REGION'],
        Settings('secrets')['AWS_LOG_GROUP'],
        Settings('secrets')['AWS_LOG_STREAM'],
    ))
    logger.setLevel(logging.INFO)
    logger.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(filename)s:%(lineno)d] -- ip: %(clientip)s, '
        'url: %(url)s, method:%(method)s')
    )
    return logger

def log_get(resource, request, payload):
    current_app.logger.info("resource requested.")

def get_secret(secret_name):
    session = boto3.session.Session()

    client = session.client(
            service_name='secretsmanager',
            region_name=Settings('secrets')['AWS_REGION'])

    secret = None

    try:
        secret = client.get_secret_value(SecretId=secret_name)

    except botocore.exceptions.ClientError as err:
        if err.response['Error']['Code'] in (
                'DecryptionFailureException',
                'InternalServiceErrorException',
                'InvalidParameterException',
                'InvalidRequestException',
                'ResourceNotFoundException'):
            Logger().error(err.response['Error']['Code'])
        else:
            return secret.get('SecretString', b64decode(secret['SecretBinary']))

    except botocoro.exceptions.ParamValidationError as error:
            Logger().error('invalid parameter: {}'.format(error))

def Main(environ, start_response):
    password = get_secret('mysql-password')
    username = get_secret('mysql-username')

    instance = Eve(logger=Logger(), settings=Settings(), validator=ValidatorSQL, data=SQL)
    instance.on_post_GET += log_get
    instance.register_blueprint(get_swagger_blueprint())
    healthcheck = EveHealthCheck(instance, '/healthcheck')

    database = instance.data.driver
    Base.metadata.bind = db.engine
    db.Model = Base 
    db.create_all()
    db.session.commit()

    def runner():
        instance.run(use_reloader=False)
         
if __name__ == '__main__':
    Main(None, None).runner()
