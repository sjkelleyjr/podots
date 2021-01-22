#!/bin/bash

# the structure of the directory and commands in this script can be found here:
#   # see this SO post for more info: https://stackoverflow.com/questions/62442212/aws-elastic-beanstalk-container-commands-failing
source /var/app/venv/*/bin/activate
cd /var/app/staging

python3 manage.py makemigrations
python3 manage.py migrate