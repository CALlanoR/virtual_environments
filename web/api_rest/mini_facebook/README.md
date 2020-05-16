# Automatically create and destroy the environment

## Compile and create the environment
bash build.sh create

## Destroy the environment (images + containers)
bash build.sh destroy

# OpenAPI Spec
http://spec.openapis.org/oas/v3.0.3

# haproxy users service api
sudo docker restart LoadBalancerServiceUsersAPI
http://localhost:7171/stats
admin:password

# haproxy publications service api
sudo docker restart LoadBalancerServiceUsersAPI
http://localhost:7272/stats
admin:password

# haproxy documentation
https://www.haproxy.com/documentation/aloha/7-5/traffic-management/lb-layer7/http-redirection/

https://www.haproxy.com/blog/using-haproxy-as-an-api-gateway-part-1/