import boto3
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


session = boto3.Session()
dynamodb = session.resource('dynamodb')
