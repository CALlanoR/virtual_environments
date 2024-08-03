import boto3

ssm_client = boto3.client('ssm')

def get_parameter(name):
    parameter = ssm_client.get_parameter(Name=name)
    return parameter['Parameter']['Value']

def update_parameter(name, value):
    ssm_client.put_parameter(
        Name=name,
        Overwrite=True,
        Value=value,
    )

def main():
    
 
if __name__ == '__main__':
    main()