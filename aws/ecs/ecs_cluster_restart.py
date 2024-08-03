import sys
import boto3
from botocore.exceptions import ClientError
 
def newTask(group, overrides, taskDefinitionArn):
    t = {}
    t['group'] = group
    t['overrides'] = overrides
    t['taskDefinitionArn'] = taskDefinitionArn
    return t
 
def stopTask(client, cluster, taskArn):
    try:
        client.stop_task(
            cluster=cluster,
            task=taskArn,
        )
    except ClientError:
        return False
    return True
 
def startTask(client, cluster, task):
    try:
        response = client.run_task(
            cluster=cluster,
            taskDefinition=task['taskDefinitionArn'],
            overrides=task['overrides'],
            count=1,
            group=task['group'],
        )
    except ClientError:
        print response
        return False
    return True
 
def main():
    if not len(sys.argv) > 1:
        print 'Please provide the cluster name to restart on as the only argument.'
        exit(1)
    cluster = sys.argv[1]
 
    client = boto3.client('ecs')
    try:
        tasks = client.list_tasks(
            cluster=cluster,
            desiredStatus='RUNNING'
        )
 
        tasksDescription = client.describe_tasks(
            cluster=cluster,
            tasks=tasks['taskArns']
        )
    except ClientError:
        print 'FAILED: Couldn\'t list running tasks, check you have exported your AWS key settings and the cluster name is correct'
        exit(1)
 
    print '-----'
    for task in tasksDescription['tasks']:
        print 'Restarting', task['taskArn'], task['group']
        print task['overrides']
        print '-----'
        # create new task definition that is a replica of already running task
        t = newTask(task['group'], task['overrides'], task['taskDefinitionArn'])
        # stop old task
        if not stopTask(client, cluster, task['taskArn']):
            print 'FAILED: couldn\'t stop task'
            exit(1)
        # start new task
        if not startTask(client, cluster, t):
            print 'FAILED: couldn\'t start task'
            exit(1)
 
if __name__ == '__main__':
    main()