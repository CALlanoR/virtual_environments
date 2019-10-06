## Automatically compile and create the environment
bash build.sh create

## Automatically destroy the environment (images + containers + volumes)
bash build.sh destroy

## Create the environment manually

## Create the environment
1. Remove all volumes, containers and images of the project
2. sudo docker-compose up -d
3. sudo docker ps -a

## Tests
3. cd java-gateway
4. python3 manual_tests.py

## Destroy all environment
1. sudo docker-compose down --rmi all