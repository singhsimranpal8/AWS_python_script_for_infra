import boto3
import time

# Create an EC2 client
ec2 = boto3.client('ec2')

# Filter instances based on tag key:Simran and value:component
response = ec2.describe_instances(Filters=[
    {'Name': 'tag-key', 'Values': ['Name']},
    {'Name': 'tag-value', 'Values': ['MyInstance']}
])

# Extract the instance IDs
instances = []
for reservation in response['Reservations']:
    for instance in reservation['Instances']:
        instances.append(instance['InstanceId'])

instance_ids = ', '.join(instances)    
# Print the instance IDs
print(', '.join(instances))
print(instance_ids)


# Set up ELB and EC2 clients
elb_client = boto3.client('elbv2')
ec2_client = boto3.client('ec2')

# Define the target group's properties
target_group_name = 'simran'
target_group_port = 80
target_group_protocol = 'HTTP'
target_group_vpc_id = 'vpc-0aff2be00876a2e88'

# Create the target group
response = elb_client.create_target_group(
    Name=target_group_name,
    Protocol=target_group_protocol,
    Port=target_group_port,
    VpcId=target_group_vpc_id
)


# Retrieve the target group's ARN
target_group_arn = response['TargetGroups'][0]['TargetGroupArn']

# Retrieve the EC2 instance ID to add to the target group
#instance_id = 'i-07cef97bdf7585ea0'

# Register the EC2 instance with the target group
response = elb_client.register_targets(
    TargetGroupArn=target_group_arn,
    Targets=[
        {
            'Id': instance_ids
        },
    ]
)

# Define the ELB's properties





elb_name = 'simran-elb'
elb_scheme = 'internet-facing'
elb_ip_address_type = 'ipv4'
elb_security_group_ids = ['sg-043670ef6a87fb908']
elb_subnet_ids = ['subnet-0b2cd3920ca03f624', 'subnet-0b1762b4023fbd3d0']

# Create the ELB
response = elb_client.create_load_balancer(
    Name=elb_name,
    Scheme=elb_scheme,
    IpAddressType=elb_ip_address_type,
    SecurityGroups=elb_security_group_ids,
    Subnets=elb_subnet_ids
)
