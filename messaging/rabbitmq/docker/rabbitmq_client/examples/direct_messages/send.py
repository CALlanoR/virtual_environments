#!/usr/bin/env python
import pika

credentials = pika.PlainCredentials('admin', 'admin')
connection = pika.BlockingConnection(pika.ConnectionParameters(
                                        'rabbitmq_server', 
                                        5672, 
                                        '/', 
                                        credentials))
channel = connection.channel()

channel.queue_declare(queue='my_queue')

channel.basic_publish(exchange='',
                      routing_key='my_queue',
                      body='Hello World!')
print(" [x] Sent 'Hello World!'")
connection.close()

