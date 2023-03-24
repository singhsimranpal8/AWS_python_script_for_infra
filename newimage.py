import boto3

# Set up an EC2 client
ec2 = boto3.client('ec2')

# Define the tag that contains the AMI ID
tag_name = 'AMI'
tag_value = 'production'

# Get the AMI ID from the specified tag
filters = [{'Name': 'tag:' + tag_name, 'Values': [tag_value]}]
images = ec2.describe_images(Filters=filters)

if len(images['Images']) == 0:
    print("No AMI found with the specified tag.")
    exit()

ami_id = images['Images'][0]['ImageId']

# Create an EC2 instance using the specified AMI ID
instance_type = 't2.micro'
key_name = 'simran'
security_group_id = 'sg-08a4f5b92da63cad7'
subnet_id = 'subnet-0b1762b4023fbd3d0'

response = ec2.run_instances(
    ImageId=ami_id,
    InstanceType=instance_type,
    KeyName=key_name,
    SecurityGroupIds=[security_group_id],
    SubnetId=subnet_id,
    MinCount=1,
    MaxCount=1,
    UserData='''#!/bin/bash
                git -C /var/www/html/bizhub-cicd-testing pull git@github.com:simranpal-webkul/bizhub-cicd-testing staging''')

# Get the instance ID of the new instance
instance_id = response['Instances'][0]['InstanceId']

# Wait for instance to be running
print("Waiting for instance to be running...")
waiter = ec2.get_waiter('instance_running')
waiter.wait(InstanceIds=[instance_id])
print("Instance is running.")

# Add the stage:staging tag to the new instance
tag_key = 'stage'
tag_value = 'staging'

ec2.create_tags(Resources=[instance_id], Tags=[{'Key': tag_key, 'Value': tag_value}])

print(f'Added tag {tag_key}:{tag_value} to instance {instance_id}')

# Get the public IP address of the new instance
instances = ec2.describe_instances(InstanceIds=[instance_id])
public_ip = instances['Reservations'][0]['Instances'][0]['PublicIpAddress']

print("Instance created with ID:", instance_id)
print("Public IP address:", public_ip)
