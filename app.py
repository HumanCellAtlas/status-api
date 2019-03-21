import boto3
import json
import logging
import re
import requests
from requests.adapters import ConnectionError

from chalice import Chalice, Response
from dcplib.aws_secret import AwsSecret
from svgs import *

app = Chalice(app_name='status-api')
dynamodb = boto3.client('dynamodb')

app.debug = True

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# API endpoints
GITLAB_SECRET = json.loads(AwsSecret('status-api/_/gitlab.json').value)

VALID_NAME = re.compile('[a-zA-Z][a-zA-Z\-0-9_.]*[a-zA-Z0-9]')
INVALID_RESPONSE = Response(status_code=406, body=json.dumps({'status': 'request_invalid'}))

route53 = boto3.client('route53')


@app.route("/availability/{service_name}", methods=["GET"])
def availability(service_name):
    if not VALID_NAME.match(service_name):
        return INVALID_RESPONSE
    service_name_no_suffix = _remove_suffix(service_name)

    row = dynamodb.get_item(
        TableName='application_statuses',
        Key={'service_name': {'S': service_name_no_suffix}}
    )

    availability_str = _recursive_get(row, 'Item', 'availability', 'N')
    availability = float(availability_str) if availability_str else availability_str
    badge_color = 'lightgrey'
    if availability:
        badge_color = 'brightgreen' if availability >= 99.999 else 'yellow' if availability >= 95.0 else 'red'

    if service_name.endswith('.svg'):
        svg = make_availability_svg(badge_color, availability)
        return Response(
            status_code=200,
            headers={
                'Content-Type': 'image/svg+xml',
                'Cache-Control': 'no-cache, no-store, max-age=0, must-revalidate'
            },
            body=svg
        )

    return Response(
        status_code=200,
        headers={
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache, no-store, max-age=0, must-revalidate'
        },
        body=dict(service_name=service_name_no_suffix, availability=availability)
    )


@app.route("/service/{service_name}", methods=["GET"])
def service(service_name):
    if not VALID_NAME.match(service_name):
        return INVALID_RESPONSE
    service_name_no_suffix = _remove_suffix(service_name)

    row = dynamodb.get_item(
        TableName='application_statuses',
        Key={'service_name': {'S': service_name_no_suffix}}
    )

    status = _recursive_get(row, 'Item', 'status', 'S')

    if service_name.endswith('.svg'):
        svg = {
            'ok': SERVICE_OK,
            'error': SERVICE_ERROR,
            None: SERVICE_UNKNOWN
        }[status]

        return Response(
            status_code=200,
            headers={
                'Content-Type': 'image/svg+xml',
                'Cache-Control': 'no-cache, no-store, max-age=0, must-revalidate'
            },
            body=svg
        )

    return Response(
        status_code=200,
        headers={
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache, no-store, max-age=0, must-revalidate'
        },
        body=dict(service_name=service_name_no_suffix, status=status)
    )


@app.route("/build/{group}/{build}/{branch}", methods=["GET"])
def build(group, build, branch):
    for param in [group, build, branch]:
        if not VALID_NAME.match(param):
            return INVALID_RESPONSE

    branch = _remove_suffix(branch)

    status_code = 200
    content_type = 'image/svg+xml'
    svg = PIPELINE_UNKNOWN
    try:
        response = requests.get(
            f"{GITLAB_SECRET['gitlab_base_url']}{group}/{build}/badges/{branch}/build.svg",
            headers={
                'PRIVATE-TOKEN': GITLAB_SECRET['gitlab_api_token']
            }
        )
        if response.status_code != 404:
            content_type = response.headers['Content-Type']
            status_code = response.status_code
            svg = response.text
    except ConnectionError:
        logger.info('Could not contact GitLab server!')

    return Response(
        status_code=status_code,
        headers={
            'Content-Type': content_type,
            'Cache-Control': 'no-cache, no-store, max-age=0, must-revalidate'
        },
        body=svg
    )


def _remove_suffix(param: str):
    return re.sub('[.]svg$', '', param)


def _recursive_get(d, *args):
    if d is None or len(args) == 0:
        return None
    if len(args) > 1:
        return _recursive_get(d.get(args[0]), *args[1:])
    else:
        return d.get(args[0])
