import logging

import boto3

log = logging.getLogger(__name__)


session = boto3.Session()
dynamodb = session.resource('dynamodb')
