import calendar
import datetime
import logging
import time
from collections import namedtuple

import boto3
from botocore.exceptions import ClientError

route53 = boto3.client('route53')
dynamodb = boto3.client('dynamodb')
cloudwatch = boto3.client('cloudwatch')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

HealthCheck = namedtuple('HealthCheck', 'name id healthy availability')


def handler(event, context):
    for health_check in _get_health_checks():
        status = "ok" if health_check.healthy else "error"
        item = dict(
            service_name={'S': health_check.name},
            status={'S': status},
            time_to_exist={'N': str(calendar.timegm(time.gmtime()) + 180)}
        )
        if health_check.availability:
            item['availability'] = dict(N=str(health_check.availability))
        dynamodb.put_item(TableName='application_statuses', Item=item)
        logger.info(f"Updated {health_check.name} ({health_check.id}) to status \"{status}\", with availability {health_check.availability}")
    logger.info("done")


def _availability(health_check_id):
    end_date = datetime.datetime.utcnow()
    start_date = end_date - datetime.timedelta(days=30)
    period = int((end_date - start_date).total_seconds())
    data = cloudwatch.get_metric_data(
        MetricDataQueries=[
            {
                'Id': "avg",
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/Route53',
                        'MetricName': 'HealthCheckPercentageHealthy',
                        'Dimensions': [
                            {
                                'Name': 'HealthCheckId',
                                'Value': health_check_id
                            },
                        ]
                    },
                    'Period': period,
                    'Stat': 'Average',
                },
                'ReturnData': True
            }
        ],
        StartTime=start_date,
        EndTime=end_date
    )['MetricDataResults']
    avg = next(ele for ele in data if ele['Id'] == 'avg')
    if len(avg['Timestamps']) < 1:
        logger.info("Skip availability calculation for {health_check_id}. This is likely a calculated health check.")
        return None
    min_ind = avg['Timestamps'].index(min(avg['Timestamps']))
    availability = avg['Values'][min_ind]
    return availability


def _find_first(f, collection):
    for ele in collection:
        if f(ele):
            return ele
    return None


def _get_health_check_status(resource_id):
    try:
        response = route53.get_health_check_status(HealthCheckId=resource_id)
    except ClientError as e:
        if e.response.get("Error", {}).get("Code") != 'Throttling':
            raise e
        seconds = 5.0
        logger.info(f"Hit rate limit. Sleeping for {seconds} seconds.")
        time.sleep(seconds)
        response = route53.get_health_check_status(HealthCheckId=resource_id)
    return all([
        ele['StatusReport']['Status'].startswith('Success')
        for ele in response['HealthCheckObservations']
    ])


def _get_health_checks():
    marker = True
    health_checks = []
    while marker:
        response = route53.list_health_checks()
        marker = response.get('NextMarker')
        health_checks += response['HealthChecks']
    health_check_ids = [ele['Id'] for ele in health_checks]

    name_mapping = dict()
    while health_check_ids:
        batch = health_check_ids[:10]
        health_check_ids = health_check_ids[10:]
        response = route53.list_tags_for_resources(ResourceType='healthcheck', ResourceIds=batch)
        for tag_set in response['ResourceTagSets']:
            resource_id = tag_set['ResourceId']
            name = _find_first(lambda s: s['Key'] == 'Name', tag_set['Tags'])
            if name:
                name_mapping[resource_id] = name['Value']

    id_health_mapping = dict()
    for health_check in [ele for ele in health_checks if ele['HealthCheckConfig']['Type'] != 'CALCULATED']:
        status = _get_health_check_status(health_check['Id'])
        health_check['Status'] = status
        id_health_mapping[health_check['Id']] = status

    calculated_health_check_ids = set([])
    for health_check in [ele for ele in health_checks if ele['HealthCheckConfig']['Type'] == 'CALCULATED']:
        calculated_health_check_ids.add(health_check['Id'])
        status = all(id_health_mapping[i] for i in health_check['HealthCheckConfig']['ChildHealthChecks'])
        id_health_mapping[health_check['Id']] = status

    return [
        HealthCheck(
            name=name_mapping[k],
            id=k,
            healthy=v,
            availability=_availability(k) if k not in calculated_health_check_ids else None
        ) for k, v in id_health_mapping.items()
    ]

