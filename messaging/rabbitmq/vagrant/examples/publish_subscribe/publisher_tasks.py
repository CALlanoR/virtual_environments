#!/usr/bin/env python
import pika
import sys

credentials = pika.PlainCredentials('admin', 'password')
connection = pika.BlockingConnection(pika.ConnectionParameters(
                                        '192.168.56.115', 
                                        5672, 
                                        '/', 
                                        credentials))
channel = connection.channel()

channel.exchange_declare(exchange='tasks',
                         type='fanout')

message = ' '.join(sys.argv[1:]) or "info: Hello World!"

channel.basic_publish(exchange='tasks',
                      routing_key='',
                      body=message)

print(" [x] Sent %r" % message)

connection.close()