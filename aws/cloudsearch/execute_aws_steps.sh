#!/bin/bash
input='{"masterfile": false, "locations":false, "hco": true, "hcp": false, "providergroups":false}'
now=$(date +"%Y%m%d_%H%M%S")
BRANCH=$1
if [ "$BRANCH" == "dev" ]; then
    ARN=arn:aws:states:us-east-1::stateMachine:update-masterfile-locations-cloudsearch-providergroups-dev
fi
if [ "$BRANCH" == "prod" ]; then
    ARN=arn:aws:states:us-east-1::stateMachine:update-masterfile-locations-cloudsearch-providergroups-prod
fi
NAME=update-masterfile-locations-cloudsearch-providergroups-$BRANCH-$now

echo -e "\033[38;5;82;1m ***** AWS Steps arn $ARN ***** \033[0;m \n"
echo -e "\033[38;5;82;1m ***** AWS Steps name $NAME ***** \033[0;m \n"

aws stepfunctions start-execution --name $NAME --state-machine-arn $ARN --input "$input"
