import json, csv, sys

class SecurityGroupRules:
    def __init__(self, client):
        self.client = client

    def get_open_sgs(self, allowed_ports):
        try:
            response = self.client.describe_security_groups()
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
        except Exception as e:
            print(e)

    def get_instances(self):
        try:
            instances = []
            instance_name = ""
            response = self.client.describe_instances()
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
        except Exception as e:
            print(e)

    def get_instance_with_open_sg_rule(self, open_sgs, instances):
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
        except Exception as e:
            print(e)
