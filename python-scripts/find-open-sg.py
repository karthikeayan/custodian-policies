import boto3
from botocore.exceptions import ClientError
import json, csv, sys
import opensg

temp_client = boto3.client('ec2')
regions = temp_client.describe_regions()
allowed_ports = ('22', '443', '80')

for region in regions['Regions']:
    region_name = region['RegionName']
    print(region_name)

    ec2 = boto3.client('ec2', region_name=region_name)
    opensg_obj = opensg.SecurityGroupRules(ec2)
    sgs = opensg_obj.get_open_sgs(allowed_ports)

    if len(sgs) > 0:
        output = csv.writer(sys.stdout)
        output.writerow(sgs[0].keys())

        for row in sgs:
            output.writerow(row.values())

    print('------------------')
