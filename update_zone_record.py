import boto3
import sys
import argparse


HOSTED_ZONE = 'Z0000000000000000000'


def set_arguments():
    """ Function for argument parser """

    parser = argparse.ArgumentParser(
        description = 'Update zone records to point this instance.')
    parser.add_argument('-v', dest = 'debug', action = 'store_true',
                        help = 'Enable verbose output. Optional')
    parser.add_argument('-4', dest = 'ipv4', help = 'IPv4 address on this instance')
    parser.add_argument('-6', dest = 'ipv6', help = 'IPv6 address on this instance')
    parser.set_defaults(debug = False)

    arguments = parser.parse_args()

    return arguments, parser


def change_zone_records(ipv4):
    """ Update the records. """

    route53_client = boto3.client('route53')
    response = route53_client.change_resource_record_sets(
        HostedZoneId=HOSTED_ZONE,
        ChangeBatch={
            'Comment': 'Update the zone records to point this instance.',
            'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': 'www.example.com',
                        'Type': 'A',
                        'TTL': 300,
                        'ResourceRecords': [
                            {
                                'Value': ipv4
                            },
                        ]
                    }
                },
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': 'example.com',
                        'Type': 'A',
                        'TTL': 300,
                        'ResourceRecords': [
                            {
                                'Value': ipv4
                            },
                        ]
                    }
                }
            ]
        }
    )

    print(response)


def main():
    args, parser = set_arguments()
    if args.ipv4 is None:
        parser.print_help()
        return -1

    change_zone_records(args.ipv4)
    print(args.ipv4)


if __name__ == "__main__":
    sys.exit(main())

