#!/usr/bin/which python3
import os
from base64 import b64decode
import logging

import boto3
import boto3.exceptions
import botocore.exceptions

from cloudwatch import CloudwatchHandler

from eve import Eve
from eve_swagger import get_swagger_blueprint, add_documentation
from eve_healthcheck import EveHealthCheck
from eve_auth_jwt import JWTAuth

from eve_sqlalchemy.validation import ValidatorSQL
from eve_sqlalchemy import SQL
from sqlalchemy.ext.declaritive import declaritive_base

from .models import Contacts

from flask import current_app

def Domain():
    return dict(contact=dict(
        item_title=str("contact"),
        description=str("Creates a contact record"),
        schema=dict(
            fullName=dict(type=str(),minlength=1,maxlength=256,required=True),
            email=dict(type=str(), minlength=4,maxlength=512,required=True)
    )))

def OpenApi(key):  
    openapi = dict(
        title=str(os.getenv('AWS_LAMBDA_FUNCTION_NAME',__file__)),
        version=str('1.0'),
        descripton=str(None),
        termsOfService=str(None),
        contact=dict(
            name=str('Dwight Spencer'),
            url=str('https://dwightaspencer.com/')),
        licence=dict(name=str('BSD'),
            url=str('https://opensource.org/licenses/BSD-2-Clause')),
        schemes=list(str('http'),str('https')))

    return openapi.get(key, openapi)

def Secrets(key):
    secrets = dict(
        AWS_KEY_ID=str(os.getenv('AWS_KEY_ID','')),
        AWS_SECRET_KEY=str(os.getenv('AWS_SECRET_KEY','')),
        AWS_REGION=str(os.getenv('AWS_REGION','')),
        AWS_LOG_GROUP=str(os.getenv('AWS_LOG_GROUP','')),
        AWS_LOG_STREAM=str(os.getenv('AWS_LOG_STREAM','')))

    return secrets.get(key, secrets)

def Settings(key):
    #'JWT_SECRET': get_secret('JWT_SECRET'), key from provider
    #'JWT_ISSUER': get_secret('JWT_ISSUER'), provider fqdn

    settings = dict(
            X_DOMAINS=list(str('*')),
            X_HEADERS=list(
                str('Origin'), 
                str('X-Requested-With'), 
                str('Content-Type'),
                str('If-Match'), 
                str('Authoriziation')),
            RENDERERS=list(str('eve.render.JSONRenderer')),
            JSON_SORT_KEYS=bool(True),
            JSONP_ARUGMENT=str('callback'),
            SCHEMA_ENDPOINT=str('/schema'),
            SWAGGER_INFO=OpenApi(),
            SWAGGER_EXAMPLE_FIELD_REMOVE=bool(True),
            TRANSPARENT_SCHEMA_RULES=bool(True),
            X_ALLOW_CREDENTIALS=bool(True),
            ITEM_METHODS=list(str('GET'), str('PATCH'), str('DELETE')),
            RESOURCE_METHODS=list(str('GET')),
            DOMAIN=Domain(),
            secrets=Secrets())

    return settings.get(key, settings)

def Logger():
    handler = CloudwatchHandler(
        Secrets('AWS_KEY_ID'),
        Secrets('AWS_SECRET_KEY'),
        Secrets('AWS_REGION'),
        Secrets('AWS_LOG_GROUP'),
        Secrets('AWS_LOG_STREAM')
    )

    logger = logging.getLogger(OpenApi('title'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(filename)s:%(lineno)d] -- ip: %(clientip)s, '
        'url: %(url)s, method:%(method)s'))

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

    except botocore.exceptions.ParamValidationError as error:
            Logger().error('invalid parameter: {}'.format(error))

def Main(environ, start_response):
    password = get_secret('mysql-password')
    username = get_secret('mysql-username')

    #instance = Eve(logger=Logger(), settings=Settings(), validator=ValidatorSQL, data=SQL, auth=JWTAuth)
    instance = Eve(logger=Logger(), settings=Settings(), validator=ValidatorSQL, data=SQL)
    instance.on_post_GET += log_get
    instance.register_blueprint(get_swagger_blueprint())
    healthcheck = EveHealthCheck(instance, '/healthcheck')

    database = instance.data.driver
    Base = declarative_base()
    Base.metadata.bind = database.engine
    database.Model = Base 
    database.create_all()
    database.session.commit()

    def runner():
        instance.run(use_reloader=False)
         
if __name__ == '__main__':
    Main(None, None).runner()
