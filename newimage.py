# for ec2 to image
import os
import boto3
from github3 import login


instance_id = 'i-0d82a0e28c5411f99'
amitag = 'copy ami from instance'

#ec2 = boto3.resource('ec2')
ec2 = boto3.client('ec2')
instance = ec2.create_image(
    InstanceId=instance_id,
    Name=amitag,
    Description='this is the AMI created from the python'
)
ami_id = instance['ImageId']
waiter = ec2.get_waiter('image_available')
waiter.wait(Filters=[{'Name': 'image-id', 'Values': [ami_id]}])
print(f'AMI {ami_id} is now available.')

# for image to ec2 
ec2_client = boto3.client('ec2')

# Retrieve your GitHub access token from the environment variables
github_access_token = os.environ.get('GITHUBACCESSTOKEN')

# Authenticate with the GitHub API using github3.py
gh = login(token=github_access_token)

# Launch EC2 instance 
response = ec2_client.run_instances(
    ImageId=ami_id,  # Replace with your desired AMI ID
    InstanceType='t2.micro',
    KeyName='simran',  # Replace with the name of your key pair
    MinCount=1,
    MaxCount=1,
    UserData='''#!/bin/bash
                git -C /var/www/html/bizhub-cicd-testing pull https://github.com/simranpal-webkul/bizhub-cicd-testing.git staging/''')


# Get instance ID
instance_id = response['Instances'][0]['InstanceId']

# Set up EC2 waiter
waiter = ec2_client.get_waiter('instance_running')

# Wait for instance to become active
waiter.wait(InstanceIds=[instance_id])

instance = ec2_client.describe_instances(InstanceIds=[instance_id])
print(f"Instance ID: {instance_id}")
print(f"Public IP address: {instance['Reservations'][0]['Instances'][0]['PublicIpAddress']}")
