from pymongo import MongoClient
import argparse
import json
import pika
import sys

def get_all_publications():
    print("View all publications...")
    client = MongoClient('mongodb://localhost:27017',
                         username='root',
                         password='example')
    db = client['publicationsDB']
    cursor = db.publications.find()
    for publication in cursor:
        print(publication)

def send_publication():
    credentials = pika.PlainCredentials('rabbitmq',
                                        'rabbitmq')
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost',
                                                                   5672,
                                                                   '/',
                                                                   credentials))
    channel = connection.channel()
    channel.exchange_declare(exchange='new_publication_event',
                             exchange_type='fanout')
    message = {
        'user_id': 1,
        'description': 'Test2'
    }
    channel.basic_publish(exchange='new_publication_event',
                          routing_key='',
                          body=json.dumps(message))
    print(" [x] Sent %r" % message,)
    connection.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--send",
                        help="send publication",
                        type=bool,
                        required=False)
    parser.add_argument("--get",
                        help="get all publications",
                        type=bool,
                        default=False)
    args = parser.parse_args()
    send = args.send
    get = args.get
    if send:
        send_publication()
    elif get:
        get_all_publications()

if __name__ == "__main__":
    main()
