import boto3
from botocore.exceptions import ClientError
import json, csv, sys

def get_open_sgs(client, allowed_ports):
    try:
        response = client.describe_security_groups()
        open_sgs = []
        cidrs = [{
                'ip_key': 'CidrIp',
                'range_key': 'IpRanges',
                'ip_format': '0.0.0.0'
            },
            {
                'ip_key': 'CidrIpv6',
                'range_key': 'Ipv6Ranges',
                'ip_format': '::/0'
            }]

        for sg in response['SecurityGroups']:
            for rule in sg['IpPermissions']:
                port = ""
                if "FromPort" in rule:
                    port = rule['FromPort']

                for cidr in cidrs:
                    for ip_range in rule[cidr['range_key']]:
                        if cidr['ip_key'] in ip_range:
                            if cidr['ip_format'] in ip_range[cidr['ip_key']]:
                                if not str(port) in allowed_ports:
                                    open_sgs.append({
                                        "name": sg['GroupName'],
                                        "id": sg['GroupId'],
                                        "source_ip" : ip_range[cidr['ip_key']],
                                        "protocol": rule['IpProtocol'],
                                        "source_port": port
                                    })
        return open_sgs
    except ClientError as e:
        print(e)

def get_instances(client):
    try:
        instances = []
        instance_name = ""
        response = client.describe_instances()
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                if "Tags" in instance:
                    for tag in instance['Tags']:
                        if tag['Key'] == 'Name':
                            instance_name = tag['Value']
                for sg in instance['SecurityGroups']:
                    instances.append({
                        'id': instance['InstanceId'],
                        'sg_id': sg['GroupId'],
                        'name': instance_name,
                    })
        return instances
    except ClientError as e:
        print(e)

def get_instance_with_open_sg_rule(client, open_sgs, instances):
    try:
        open_instances = []
        for instance in instances:
            for sg in open_sgs:
                if instance['sg_id'] in sg['id']:
                    open_instances.append({
                        'instance_id': instance['id'],
                        'instance_name': instance['name'],
                        'sg_id': sg['id'],
                        'sg_name': sg['name'],
                        'sg_source_ip': sg['source_ip'],
                        'sg_port': sg['source_port'],
                        'sg_protocol': sg['protocol']
                    })
        return open_instances
    except ClientError as e:
        print(e)

allowed_ports = ("22", "80", "443")
temp_client = boto3.client('ec2')
regions = temp_client.describe_regions()

for region in regions['Regions']:
    region_name = region['RegionName']
    print(region_name)

    ec2 = boto3.client('ec2', region_name=region_name)

    sgs = get_open_sgs(ec2, allowed_ports)
    # instances = get_instances(ec2)

    # open_instances = get_instance_with_open_sg_rule(ec2, sgs, instances)

    if len(sgs) > 0:
        output = csv.writer(sys.stdout)
        output.writerow(sgs[0].keys())

        for row in sgs:
            output.writerow(row.values())

    print('------------------')
