import calendar
import logging
import time

import boto3
from botocore.exceptions import ClientError

route53 = boto3.client('route53')
dynamodb = boto3.client('dynamodb')

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    mappings = _get_tag_mappings()
    for service_name, resource_id in mappings.items():
        try:
            response = route53.get_health_check_status(HealthCheckId=resource_id)
        except ClientError as e:
            if e.response.get("Error", {}).get("Code") == 'Throttling':
                seconds = 2.0
                logger.info(f"Hit rate limit. Sleeping for {seconds} seconds.")
                time.sleep(seconds)
                response = route53.get_health_check_status(HealthCheckId=resource_id)
            elif e.response.get("Error", {}).get("Code") != 'InvalidInput':
                raise e
            else:
                # Do not fail if this is an aggregated health check
                logger.info(f"Skipping {service_name}")
                continue

        healthy = all([
            ele['StatusReport']['Status'].startswith('Success')
            for ele in response['HealthCheckObservations']
        ])
        status = "ok" if healthy else "error"
        dynamodb.put_item(
            TableName='application_statuses',
            Item={
                'service_name': {'S': service_name},
                'status': {'S': status},
                'time_to_exist': {'N': str(calendar.timegm(time.gmtime()) + 180)}
            }
        )
        logger.info(f"Updated {service_name} to status \"{status}\"")
    logger.info("done")


def _find_first(f, collection):
    for ele in collection:
        if f(ele):
            return ele
    return None


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
            resource_id = tag_set['ResourceId']
            name = _find_first(lambda s: s['Key'] == 'Name', tag_set['Tags'])
            if name:
                mapping[name['Value']] = resource_id
    return mapping
