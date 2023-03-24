import boto3

# Define your EC2 client
ec2 = boto3.client('ec2')

# Define your ELBv2 client
elbv2 = boto3.client('elbv2')

# Define your target group ARN
target_group_arn = 'arn:aws:elasticloadbalancing:ap-northeast-1:778611821858:targetgroup/simran/adb99844b9793738'

# Get all instances with the tag "stage:production"
response = ec2.describe_instances(Filters=[
        {
            'Name': 'tag:stage',
            'Values': ['production']
        }
    ])

# Extract the instance IDs with the "stage:production" tag
instance_ids = [instance['InstanceId'] for reservation in response['Reservations'] for instance in reservation['Instances']]

if instance_ids:
    # Register the instance(s) with the target group
    elbv2.register_targets(
        TargetGroupArn=target_group_arn,
        Targets=[
            {'Id': instance_id}
            for instance_id in instance_ids
        ]
    )

    # Wait for the instances to reach a healthy state in the target group
    print('Waiting for instances to reach a healthy state...')
    waiter = elbv2.get_waiter('target_in_service')
    waiter.wait(TargetGroupArn=target_group_arn)

    # Deregister any instances not with the "stage:production" tag
    instances = elbv2.describe_target_health(TargetGroupArn=target_group_arn)["TargetHealthDescriptions"]
    instances_with_tag = []
    for instance in instances:
        instance_id = instance["Target"]["Id"]
        tags = ec2.describe_tags(Filters=[{"Name": "resource-id", "Values": [instance_id]}])["Tags"]
        if any(tag["Key"] == "stage" and tag["Value"] == "production" for tag in tags):
            instances_with_tag.append(instance_id)

    for instance in instances:
        instance_id = instance["Target"]["Id"]
        if instance_id not in instances_with_tag:
            print(f"Instance {instance_id} removed from target group.")
            elbv2.deregister_targets(TargetGroupArn=target_group_arn, Targets=[{"Id": instance_id}])
else:
    print('No instances with the "stage:production" tag found.')
