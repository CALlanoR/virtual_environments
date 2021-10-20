#!/usr/bin/env python
import pika

credentials = pika.PlainCredentials('admin', 'admin')
connection = pika.BlockingConnection(pika.ConnectionParameters(
                                        'rabbitmq_server', 
                                        5672, 
                                        '/', 
                                        credentials))
channel = connection.channel()

channel.exchange_declare(exchange='neworder',
                         exchange_type='fanout')

result = channel.queue_declare(queue='',
                               durable=True)
queue_name = result.method.queue

channel.queue_bind(exchange='neworder',
                   queue=queue_name)

print(' [*] Waiting for New Orders. To exit press CTRL+C')

def callback(ch, method, properties, body):
    print(" [x] %r" % body)

channel.basic_consume(queue=queue_name, 
                      on_message_callback=callback,
                      auto_ack=True)

channel.start_consuming()
