#!/bin/bash

regions=("us-east-1" "us-east-2" "us-west-1" "us-west-2" "ca-central-1" "eu-central-1" "eu-west-1" "eu-west-2" "eu-west3" "eu-north-1" \
	 "ap-northeast-1" "ap-northeast-2" "ap-northeast-3" "ap-southeast-1" "ap-southeast-2" "ap-south-1" "sa-east-1")

for region in ${regions[*]}; do
  echo "Replacing region with in ${region} in config file"
  echo ""
  sed -i "3s/^region\ =\ .*$/region\ =\ ${region}/g" ~/.aws/config
  echo "Deplying in ${region}"
  echo ""
  $1
  cat ~/.aws/config
  echo "---------"
done
