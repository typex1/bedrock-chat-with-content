#!/bin/bash
# to be used as Amazon EC2 user data or run manually:
sudo yum update -y
sudo yum install git -y
sudo yum install tree -y
sudo su - ec2-user
su - ec2-user -c 'wget https://bootstrap.pypa.io/get-pip.py && python3 get-pip.py'
