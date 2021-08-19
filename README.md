# Twitter analyzer to AWS cloud

I want to trigger a process from authenticated machine. After the process is finished
there should be Kibana dashboard where I can study twitter trends in the given spaces.

## Step 1: Automatically terminate the EC2 instance

The EC2 instance hosting the elasticsearch node (Single node cluster) should terminate it self
after the predefined time. Source: https://alestic.com/2010/09/ec2-instance-termination/

### EC cli commands

Curl command for fetching the instance ID number

    $ TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"`
    $ curl -H "X-aws-ec2-metadata-token: $TOKEN" -v http://169.254.169.254/latest/meta-data/instance-id
    $ curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/placement/region

AWS cli command for terminating an instance

    > aws ec2 terminate-instances --instance-ids aaaaaaa
    $ echo "aws ec2 terminate-instances --instance-ids i-0bf6db79f0766868e --region eu-central-1" |at now + 123 min

### Prerequisites

For the aws cli to work the instance must be assosiated with a proper instance profile. Especially
the instance myst have permissions to _ec2:TerminateInstances_. I have created a CloudFormation
stack that creates a suitable plicy and instance profile. The profile also allows the use of
EC2 instance connect. The stack template can be found in this directory with the name:
server-instance-role.yml

## Step 2: Configure kibana

Kibana configuration lies in _/etc/kibana/kibana.yml_. One should add followin rows to the config:

        server.port: 5601
        server.host: "0.0.0.0"

This allows you to access kibana over the internet. Note that ElasticSearch doesn't require
configuration changes. It runs in the same host than kibana and the tweet_fecher is run locally. It
is possible that changing the password requires something..

## Step 3: Aquire a domain and SSL certificate

Planning to use Route53 for the Domain. Cheapest ones are $5 per year. The integration should
be easy enough. For the SSL certificate there are two options:

- let's encrypt
- AWS cert manager

## Step 4: Automate tweet_fetcher :)

Just do it.

