import boto3
import json
import logging
import re
import requests
import retrying

from chalice import Chalice, Response
from dcplib.aws_secret import AwsSecret
from cache import global_cache
from svgs import *

app = Chalice(app_name='status-api')

app.debug = True

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# API endpoints
GITLAB_SECRET = json.loads(AwsSecret('status-api/_/gitlab.json').value)

VALID_NAME = re.compile('[a-zA-Z][a-zA-Z\-0-9_.]*[a-zA-Z0-9]')
INVALID_RESPONSE = Response(status_code=406, body=json.dumps({'status': 'request_invalid'}))

route53 = boto3.client('route53')


@app.route("/service/{service_name}", methods=["GET"])
def service(service_name):
    global MAPPING_CACHE

    if not VALID_NAME.match(service_name):
        return INVALID_RESPONSE

    service_name = _remove_suffix(service_name)

    rId = _get_tag_mappings().get(service_name)

    if not rId:
        return Response(
            status_code=200,
            headers={
                'Content-Type': 'image/svg+xml'
            },
            body=SERVICE_UNKNOWN
        )

    response = _get_health_check_status(rId)
    healthy = all([
        ele['StatusReport']['Status'].startswith('Success')
        for ele in response['HealthCheckObservations']
    ])
    return Response(
        status_code=200,
        headers={
            'Content-Type': 'image/svg+xml'
        },
        body=SERVICE_OK if healthy else SERVICE_ERROR
    )


@app.route("/build/{group}/{build}/{branch}", methods=["GET"])
def build(group, build, branch):
    for param in [group, build, branch]:
        if not VALID_NAME.match(param):
            return INVALID_RESPONSE

    branch = _remove_suffix(branch)

    response = requests.get(
        f"{GITLAB_SECRET['gitlab_base_url']}{group}/{build}/badges/{branch}/build.svg",
        headers={
            'PRIVATE-TOKEN': GITLAB_SECRET['gitlab_api_token']
        }
    )
    return Response(
        status_code=response.status_code,
        headers={
            'Content-Type': response.headers['Content-Type']
        },
        body=response.text
    )


def _remove_suffix(param):
    return re.sub('[.]svg$', '', param)


def _find_first(f, collection):
    for ele in collection:
        if f(ele):
            return ele
    return None


@global_cache(ttl=60)
def _get_tag_mappings():
    health_check_ids = _get_health_check_ids()
    return _ids_to_tag_mappings(health_check_ids)


def _get_health_check_ids():
    marker = True
    health_check_ids = []
    while marker:
        response = route53.list_health_checks()
        marker = response.get('NextMarker')
        health_check_ids += [ele['Id'] for ele in response['HealthChecks']]
    return health_check_ids


def _ids_to_tag_mappings(health_check_ids):
    mapping = dict()
    while health_check_ids:
        batch = health_check_ids[:10]
        health_check_ids = health_check_ids[10:]
        response = route53.list_tags_for_resources(
            ResourceType='healthcheck',
            ResourceIds=batch
        )
        for tag_set in response['ResourceTagSets']:
            rId = tag_set['ResourceId']
            name = _find_first(lambda s: s['Key'] == 'Name', tag_set['Tags'])
            if name:
                mapping[name['Value']] = rId
    return mapping


@global_cache(ttl=60)
def _get_health_check_status(rId):
    return route53.get_health_check_status(HealthCheckId=rId)
