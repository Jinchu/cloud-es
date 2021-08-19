""" Script for launching an ElasticSearch server for analysing tweets. """

import base64
import sys
import argparse
import boto3

SG_ID = "sg-0b0c5eab3757aeaaa"
INSTANCE_SIZE = "t3a.xlarge"
AMI = "ami-06f80b401890be7ec"

USERDATA_PATH = './self-terminate.bash'
SERVER_NAME = 'Twitter-ElasticSearch'
SPOT_PRICE = "0.0632"
INSTANCE_PROFILE = 'arn:aws:iam::670000000000:instance-profile/ElasticSearchServerInstanceProfile'

def set_arguments():
    """ Function for argument parser """

    parser = argparse.ArgumentParser(
        description = 'Launch ElasticSearch server for analysing tweets.')
    parser.add_argument('-v', dest = 'debug', action = 'store_true',
                        help = 'Enable verbose output. Optional')
    parser.add_argument('-spot', dest = 'spot', action = 'store_true',
                        help = 'Use spot instance instead of on-demand..')
    parser.set_defaults(debug = False, spot = False)

    arguments = parser.parse_args()

    return arguments, parser


def get_tags():
    """ Get standard tags for anything in this script. """
    tag_list = [
        {
            'Key': 'Project',
            'Value': 'Twitter-Analysis'
        },
        {
            'Key': 'Name',
            'Value': SERVER_NAME
        }
    ]

    return tag_list


class ElasticSearchServerInstance():
    """ Context for AWS API calls. """
    def __init__(self, debug=False) -> None:
        self.debug_mode = debug

    def launch_server(self, use_spot):
        """ Sends the command to AWS api to launch a spot instance that will self destruct. """

        with open(USERDATA_PATH, 'rb') as handle:
            user_data_b = handle.read()
        user_data_b64 = base64.b64encode(user_data_b)
        if self.debug_mode:
            user_d_str = user_data_b64.decode('utf-8')
            print(f'user-data: {user_d_str}')

        if use_spot:
            ec2_cli = boto3.client('ec2')
            response = ec2_cli.request_spot_instances(
                LaunchSpecification={
                    'IamInstanceProfile': {
                        'Arn': INSTANCE_PROFILE,
                    },
                    'ImageId': AMI,
                    'InstanceType': INSTANCE_SIZE,
                    'SecurityGroupIds': [
                        SG_ID,
                    ],
                    'KeyName': 'aws-frankfurt-2',
                    'UserData': user_data_b64.decode('utf-8')
                },
                SpotPrice=SPOT_PRICE,
                Type='one-time',
                TagSpecifications=[
                    {
                        'ResourceType': 'spot-instances-request',
                        'Tags': get_tags()
                    }
                ]
            )
            return response["SpotInstanceRequests"][0]["SpotInstanceRequestId"]

        ec2_resource = boto3.resource('ec2')
        response = ec2_resource.create_instances(
            ImageId=AMI,
            InstanceType=INSTANCE_SIZE,
            CreditSpecification ={
                'CpuCredits': 'standard'
            },
            MinCount=1, MaxCount=1,
            UserData=user_data_b64.decode('utf-8'),
            SecurityGroupIds=[SG_ID],
            Ipv6AddressCount=1,
            KeyName='aws-frankfurt-2',
            IamInstanceProfile={
                'Arn': INSTANCE_PROFILE
            },
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': get_tags()
                }
            ]
            )

        print(response[0])
        return response[0]


def main():
    """ Main """
    args, parser = set_arguments()

    es_server = ElasticSearchServerInstance(debug=args.debug)

    request_id = es_server.launch_server(use_spot=args.spot)
    if args.debug:
        print('SpotInstanceRequestId: {}'.format(request_id))


if __name__ == "__main__":
    sys.exit(main())
