#!/usr/bin/env python3
import requests
from environs import Env
import boto3
import botocore
import threading

interval = 15.0
drone_token = ""
drone_server = ""
metric_namespace = ""

def main():
    global interval
    global drone_token
    global drone_server
    global metric_namespace

    env = Env()
    env.read_env()
    drone_server = env("DRONE_SERVER")
    drone_token = env.str("DRONE_TOKEN", "")
    interval = env.float("PUSH_INTERVAL",15.0)
    metric_namespace = env.str("METRIC_NAMESPACE", "Drone-Server")
    scrape_and_push()

def scrape_and_push():
    threading.Timer(interval, scrape_and_push).start()
    request_headers = None
    if drone_token != "":
        request_headers = {'Authorization': "Bearer %s" % drone_token}
    r = requests.get("%s/api/system/stats" % drone_server, headers=request_headers)
    if r.status_code == 401:
        print("Unauthorize to  call api")
        exit(1)

    json_data = r.json()
    print("Builds Pending: %s" % json_data['builds']['pending'], flush=True)
    send_metric(json_data['builds']['pending'],metric_namespace,drone_server)

def send_metric(builds_pending,namespace,drone_server):
    try:
        cw = boto3.client('cloudwatch')
        response = cw.put_metric_data(
        MetricData=[
            {
                'MetricName': 'PendingBuilds',
                'Dimensions': [
                    {
                        'Name': 'Server',
                        'Value': drone_server
                    },
                ],
                'Unit': 'None',
                'Value': builds_pending
            },
        ],
        Namespace=namespace
        )
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            print("Error putting metric: \n%s" % response, flush=True)
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "AccessDenied":
            print("Access Denied: %s" % e, flush=True)
            exit(1)
        else:
            raise
    except botocore.exceptions.NoCredentialsError as er:
        exit(1)

if __name__ == "__main__":
    main()