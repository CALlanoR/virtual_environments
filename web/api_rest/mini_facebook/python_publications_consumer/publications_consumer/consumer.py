from pymongo import MongoClient
import json
import pika

def _save_publication_in_database(publication):
    client = MongoClient('mongodb://localhost:27017',
                         username='root',
                         password='example')
    db = client['publicationsDB']
    result = db.publications.insert_one(publication)
    print('One post: {0}'.format(result.inserted_id))

def main():
    credentials = pika.PlainCredentials('rabbitmq',
                                        'rabbitmq')
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 
                                                                    5673, 
                                                                    '/', 
                                                                    credentials))
    channel = connection.channel()
    channel.exchange_declare(exchange='new_publication_event',
                            exchange_type='fanout')

    result = channel.queue_declare(queue='',
                                exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange='new_publication_event',
                    queue=queue_name)

    def callback(ch, method, properties, body):
        publication = json.loads(body)
        _save_publication_in_database(publication)

    channel.basic_consume(queue=queue_name,
                        on_message_callback=callback,
                        auto_ack=True)

    channel.start_consuming()

if __name__ == "__main__":
    main()

