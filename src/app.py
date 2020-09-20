
import os
import base64
import logging

from boto3 import *
from cloudwatch import CloudwatchHandler

#from sql

from eve import Eve
from eve_swagger import get_swagger_blueprint, add_documentation
from eve_healthcheck import EveHealthCheck

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
        'title': 'lambda-api-hubspot',
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
            'X_HEADERS': ['Content-Type', 'If-Match', 'Authorization'],
            'RENDERERS': ['eve.render.JSONRenderer'],
            'JSON_SORT_KEYS': True,
            'JSONP_ARGUMENT': 'callback',
            'SCHEMA_ENDPOINT ': '/schema',
            'SWAGGER_INFO':  OpenApi(),
            'SWAGGER_EXAMPLE_FIELD_REMOVE': True,
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
    logger = logging.getLogger(os.getenv('AWS_LAMBDA_FUNCTION_NAME',__file__))
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
    client = session.client(service_name=os.environ['AWS_LAMBDA_FUNCTION_NAME'],
            region_name=Settings('secrets')['AWS_REGION'])

    secret = None

    try:
        secret = client.get_secret_value(SecretId=secret_name)
    except ClientError as err:
        if err.response['Error']['Code'] in (
                'DecryptionFailureException',
                'InternalServiceErrorException',
                'InvalidParameterException',
                'InvalidRequestException',
                'ResourceNotFoundException'):
            current_app.logger.error(err.response['Error']['Code'])
        else:
            return secret.get('SecretString', b64decode(secret['SecretBinary']))

def Main(environ, start_response):
    instance = Eve(logger=Logger(), settings=Settings())
    instance.on_post_GET += log_get
    instance.register_blueprint(get_swagger_blueprint())

    healthcheck = EveHealthCheck(instance, '/healthcheck')

    instance.run()
         
if __name__ == '__main__':
    Main()
