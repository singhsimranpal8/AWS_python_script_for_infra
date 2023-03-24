import boto3

# Create EC2 client
ec2 = boto3.client('ec2')

# Set the tag key and value to search for
tag_key = 'AMI'
tag_value = 'production'

# Get all AMIs with the specified tag
response = ec2.describe_images(Filters=[{'Name': f'tag:{tag_key}', 'Values': [tag_value]}])
images = response['Images']

# Remove the tag from each AMI
for image in images:
    ami_id = image['ImageId']
    ec2.delete_tags(Resources=[ami_id], Tags=[{'Key': tag_key, 'Value': tag_value}])
    print(f'Removed tag {tag_key}:{tag_value} from AMI {ami_id}')


# Create EC2 client
ec2 = boto3.client('ec2')

# Set the tag key and value to search for
tag_key = 'stage'
tag_value = 'staging'

# Get the instance ID of the first instance with the specified tag
response = ec2.describe_instances(Filters=[{'Name': f'tag:{tag_key}', 'Values': [tag_value]}])
instances = response['Reservations'][0]['Instances']
instance_id = instances[0]['InstanceId']


# Create a new AMI from the instance
response = ec2.create_image(InstanceId=instance_id, Name='AMI Name', Description='AMI Description')

# Get the new AMI ID
ami_id = response['ImageId']

# Add the AMI:production tag to the new AMI
ec2.create_tags(Resources=[ami_id], Tags=[{'Key': 'AMI', 'Value': 'production'}])

print(f'Created new AMI {ami_id} from instance {instance_id}')

# Wait for the new AMI to be available
waiter = ec2.get_waiter('image_available')
waiter.wait(Filters=[{'Name': 'image-id', 'Values': [ami_id]}])
print(f'AMI {ami_id} is now available')


# Create EC2 client
ec2 = boto3.client('ec2')

# Set the tag key and value to search for
tag_key = 'stage'
tag_value = 'production'

# Get all instances with the specified tag
response = ec2.describe_instances(Filters=[{'Name': f'tag:{tag_key}', 'Values': [tag_value]}])
reservations = response['Reservations']

# Loop through all instances with the tag and remove the tag
for reservation in reservations:
    instances = reservation['Instances']
    for instance in instances:
        instance_id = instance['InstanceId']
        ec2.delete_tags(Resources=[instance_id], Tags=[{'Key': tag_key}])
        print(f'Removed tag {tag_key} from instance {instance_id}')


# Create a new instance from the new AMI

response = ec2.run_instances(ImageId=ami_id, InstanceType='t2.micro', MinCount=1, MaxCount=1)

# Get the new instance ID
instance_id = response['Instances'][0]['InstanceId']
print(f'Created new instance {instance_id} from AMI {ami_id}')

# Wait for the new instance to be running
waiter = ec2.get_waiter('instance_running')
waiter.wait(InstanceIds=[instance_id])
print(f'Instance {instance_id} is now running')

# Add the stage:production tag to the new instance
tag_key = 'stage'
tag_value = 'production'

ec2.create_tags(Resources=[instance_id], Tags=[{'Key': tag_key, 'Value': tag_value}])

print(f'Added tag {tag_key}:{tag_value} to instance {instance_id}')



# Create EC2 and EIP client objects
ec2_client = boto3.client('ec2')
eip_client = boto3.client('ec2')

# Search for Elastic IP with value 62.62.62.62
response = eip_client.describe_addresses(
    Filters=[
        {
            'Name': 'public-ip',
            'Values': [
                '54.250.164.197',
            ]
        },
    ]
)

if response['Addresses']:
    eip_allocation_id = response['Addresses'][0]['AllocationId']
    print(f"Found Elastic IP: {eip_allocation_id}")

    # Check if Elastic IP is associated with an instance
    if 'AssociationId' in response['Addresses'][0]:
        association_id = response['Addresses'][0]['AssociationId']
        print(f"Elastic IP {eip_allocation_id} is currently associated with instance: {response['Addresses'][0]['InstanceId']}")

        # Disassociate Elastic IP from instance
        ec2_client.disassociate_address(
            AssociationId=association_id
        )

    # Search for EC2 instances with stage:production tag
    instances = ec2_client.describe_instances(
        Filters=[
            {
                'Name': 'tag:stage',
                'Values': [
                    'production',
                ]
            },
            {
                'Name': 'instance-state-name',
                'Values': [
                    'running',
                ]
            }
        ]
    )

    if instances['Reservations']:
        # Get the first instance found
        instance_id = instances['Reservations'][0]['Instances'][0]['InstanceId']
        print(f"Found EC2 instance: {instance_id}")

        # Associate Elastic IP with EC2 instance
        ec2_client.associate_address(
            AllocationId=eip_allocation_id,
            InstanceId=instance_id
        )
    else:
        print("No running instances with the 'stage:production' tag were found.")
else:
    print("Elastic IP address 54.250.164.197 was not found.")
    
