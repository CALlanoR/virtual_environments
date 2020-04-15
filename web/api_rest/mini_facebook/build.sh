#!/bin/sh
ACTION=$1
if [ "$ACTION" == "create" ]; then

    tput setaf 2; tput bold; echo "**** creating all environment with docker-compose ****"
    tput setaf 7; tput sgr0

    # Create environment
    sudo docker-compose up -d

    tput setaf 2; tput bold; echo "**** listing containers created ****"
    tput setaf 7; tput sgr0

    # Verify
    sudo docker ps -a

    tput setaf 2; tput bold; echo "**** database ipaddress ****"
    tput setaf 7; tput sgr0

    # Get the database ipaddress
    sudo docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' MySQLServiceDB
else
    if [ "$ACTION" == "destroy" ]; then
        tput setaf 1; tput bold;  echo "**** destroying environment ****"
        tput setaf 7; tput sgr0

        # Destroy the environment
        # sudo docker-compose down --rmi all
        sudo docker-compose down --rm all

        tput setaf 1; tput bold;  echo "**** remove all unused local volumes ****"
        tput setaf 7; tput sgr0
        read -p "Do you wish to remove all unused local volumes? " yn
            case $yn in
                [Yy]* ) sudo docker volume prune;;
                [Nn]* ) exit;;
                * ) echo "Please answer yes or no.";;
            esac
    else
        tput setaf 1; tput bold; echo "${red} action $ACTION not supported"
        tput setaf 7; tput sgr0
    fi
fi