from pymongo import MongoClient
from configparser import ConfigParser
import json
import pika

def _save_publication_in_database(publication):
    print('publication: {0}'.format(str(publication)))
    client = MongoClient(_get_property('mongodb','url'),
                         username=_get_property('mongodb','username'),
                         password=_get_property('mongodb','password'))
    db = client[_get_property('mongodb','database')]
    result = db.publications.insert_one(publication)
    print('One post: {0}'.format(result.inserted_id))

def main():
    credentials = pika.PlainCredentials(_get_property('rabbitmq','user'),
                                        _get_property('rabbitmq','password'))
    connection = pika.BlockingConnection(pika.ConnectionParameters(_get_property('rabbitmq','url'),
                                                                   int(_get_property('rabbitmq','port')),
                                                                   '/',
                                                                   credentials))
    channel = connection.channel()
    channel.exchange_declare(exchange=_get_property('rabbitmq','exchange'),
                             exchange_type='fanout')

    result = channel.queue_declare(queue='',
                                   exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=_get_property('rabbitmq','exchange'),
                       queue=queue_name)

    def callback(ch, method, properties, body):
        print('body: {0}'.format(str(body)))
        publication = json.loads(body)
        _save_publication_in_database(publication)

    channel.basic_consume(queue=queue_name,
                          on_message_callback=callback,
                          auto_ack=True)

    channel.start_consuming()

def _get_property(context, property_name):
    config = ConfigParser()
    config.read('config.ini')
    return config.get(context, property_name)

if __name__ == "__main__":
    main()
