import boto3

elbv2_client = boto3.client('elbv2', region_name='ap-northeast-1')

target_group_arn = 'arn:aws:elasticloadbalancing:ap-northeast-1:778611821858:targetgroup/simran/b8ed698d4169716c'
new_instance_id = 'i-07a862f33d558f807'
new_instance_port = 80

# Get the list of registered targets for the target group
response = elbv2_client.describe_target_health(TargetGroupArn=target_group_arn)
registered_targets = response['TargetHealthDescriptions']

# If there are any registered targets, remove the first one
if registered_targets:
    old_instance_id = registered_targets[0]['Target']['Id']
    response = elbv2_client.deregister_targets(
        TargetGroupArn=target_group_arn,
        Targets=[
            {
                'Id': old_instance_id
            }
        ]
    )
    print(f'Removed old instance {old_instance_id} from target group {target_group_arn}')

# Add the new instance to the target group
response = elbv2_client.register_targets(
    TargetGroupArn=target_group_arn,
    Targets=[
        {
            'Id': new_instance_id,
            'Port': new_instance_port
        }
    ]
)
print(f'Added new instance {new_instance_id} to target group {target_group_arn}')
