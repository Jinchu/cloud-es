#!/bin/bash
set -x

TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 3600"`
INSTANCE_ID=`curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id`
REGION=`curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/placement/region`

sudo yum update -y

echo $INSTANCE_ID 'in' $REGION

echo "aws ec2 terminate-instances --instance-ids $INSTANCE_ID --region $REGION" |at now + 185 min

sudo yum -y install htop git python3-pip jq
sudo pip3 install tweepy boto3
python3 -m pip install elasticsearch==7.8.1

aws s3 cp s3://internal-obryarddangosd/twitter-analysis/update_zone_record.py .
IPV4=`curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/public-ipv4`
python3 update_zone_record.py -4 $IPV4

cd /etc/
aws s3 cp s3://internal-obryarddangosd/twitter-analysis/letsencrypt.tar.gz .
tar xf letsencrypt.tar.gz
chown -R kibana:kibana /etc/letsencrypt

cd ~
aws s3 cp s3://internal-obryarddangosd/twitter-analysis/kibana.yml /etc/kibana/kibana.yml
aws s3 cp s3://internal-obryarddangosd/twitter-analysis/internal_users.yml /usr/share/elasticsearch/plugins/opendistro_security/securityconfig/internal_users.yml

sudo /bin/systemctl daemon-reload
sudo /bin/systemctl enable elasticsearch.service
sudo /bin/systemctl start elasticsearch.service
sleep 3
/usr/share/elasticsearch/plugins/opendistro_security/tools/securityadmin.sh -cd /usr/share/elasticsearch/plugins/opendistro_security/securityconfig/ -icl -nhnv -cacert /etc/elasticsearch/root-ca.pem -cert /etc/elasticsearch/kirk.pem -key /etc/elasticsearch/kirk-key.pem

sleep 3
sudo systemctl start kibana.service

mkdir analysis
cd analysis
git clone https://github.com/Jinchu/analyse_twitter.git
aws s3 cp s3://internal-obryarddangosd/twitter-analysis/infosec_user_ids.txt .
aws s3 cp s3://internal-obryarddangosd/twitter-analysis/twitter.conf .

ELA_PASSWORD=`aws ssm get-parameter --region $REGION --name elasticSearch_password --with-decryption |jq ".Parameter.Value"`
ELASTICSEARCH_PASSWORD="${ELA_PASSWORD%\"}"
ELASTICSEARCH_PASS="${ELASTICSEARCH_PASSWORD#\"}"

export ELASTICSEARCH_PASS
python3 analyse_twitter/tweet_fetcher/ -m list -c ./twitter.conf
