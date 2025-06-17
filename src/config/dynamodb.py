import logging

import boto3

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


session = boto3.Session()
dynamodb = session.resource('dynamodb')
