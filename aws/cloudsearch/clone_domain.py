#!/bin/bash
#
# Usage: cloudsearch-clone-domain <domain> <newdomain>
# Example: ./clone_domain.sh search-hco-prod hco-prod

die () {
    echo >&2 "$@"
    exit 1
}
[ "$#" -eq 2 ] || die "Usage: cloudsearch-clone-domain <domain> <newdomain>"

# ============================================ Step #1 (Create new domain) =========================================== #

echo -e "\033[38;5;82;1m **** Creating domain $2... **** \033[0;m \n"
aws cloudsearch create-domain --domain-name $2

status=$(aws cloudsearch describe-domains --domain-names $2 | jq -r '.[] | .[] | .Processing')
i=1
sp="/-\|"
echo -n ' '
while [ "$status" == "true" ]; do
    sleep 1m
    status=$(aws cloudsearch describe-domains --domain-names $2 | jq -r '.[] | .[] | .Processing')
    printf "\b${sp:i++%${#sp}:1}"
done
echo -e "\033[38;5;82;1m **** Domain $2 created... **** \033[0;m \n"

# ============================================ Step #2 (Update instance type) ======================================== #

echo -e "\033[38;5;82;1m **** Updating desired instance type in domain $2... **** \033[0;m \n"
aws cloudsearch update-scaling-parameters --domain-name hco-prod --scaling-parameters DesiredInstanceType=search.xlarge

echo -e "\033[38;5;82;1m **** Running process in domain $2... **** \033[0;m \n"
aws cloudsearch index-documents --domain-name hco-prod

status=$(aws cloudsearch describe-domains --domain-names $2 | jq -r '.[] | .[] | .Processing')
i=1
sp="/-\|"
echo -n ' '
while [ "$status" == "true" ]; do
    sleep 1m
    status=$(aws cloudsearch describe-domains --domain-names $2 | jq -r '.[] | .[] | .Processing')
    printf "\b${sp:i++%${#sp}:1}"
done

echo -e "\033[38;5;82;1m **** Desired instance type $2 updated... **** \033[0;m \n"

# ============================================ Step #3 (Get current domain indixes) ================================== #

echo -e "\033[38;5;82;1m **** Getting information from the $1 domain indixes... **** \033[0;m \n"
aws cloudsearch describe-index-fields --domain $1 | jq ".[][] | {\"DomainName\": \"$2\", \"IndexField\": .Options} | tostring" | sed 's/^/aws cloudsearch define-index-field --cli-input-json /' > define-fields-$2.sh
chmod +x define-fields-$2.sh

echo -e "\033[38;5;82;1m **** Running script to duplicate domain indixes... **** \033[0;m \n"
sh ./define-fields-$2.sh

echo -e "\033[38;5;82;1m **** Running process in domain $2... **** \033[0;m \n"
aws cloudsearch index-documents --domain-name $2

status=$(aws cloudsearch describe-domains --domain-names $2 | jq -r '.[] | .[] | .Processing')
i=1
sp="/-\|"
echo -n ' '
while [ "$status" == "true" ]; do
    sleep 1m
    status=$(aws cloudsearch describe-domains --domain-names $2 | jq -r '.[] | .[] | .Processing')
    printf "\b${sp:i++%${#sp}:1}"
done

echo -e "\033[38;5;82;1m ****Process completed... **** \033[0;m \n"

# ============================================ End =================================================================== #