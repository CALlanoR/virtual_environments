from app import app
import db_config
import pika
import json
import sys
from datetime import datetime
from repositories.PublicationsRepository import PublicationsRepository

class PublicationsService(object):
    def __init__(self):
        self.publications_repository = PublicationsRepository()

    def send_publication(self,
                         publication):
        try:
            credentials = pika.PlainCredentials(app.config['rabbitmq_user'],
                                                app.config['rabbitmq_password'])
            connection = pika.BlockingConnection(pika.ConnectionParameters(app.config['rabbitmq_host'],
                                                                           app.config['rabbitmq_port'],
                                                                           '/',
                                                                           credentials))
            channel = connection.channel()
            channel.exchange_declare(exchange=app.config['rabbitmq_exchange'],
                                    exchange_type='fanout')

            today = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            publication['publication_date'] = str(today)
            print(publication)
            print("publication {0}".format(publication))
            channel.basic_publish(exchange=app.config['rabbitmq_exchange'],
                                routing_key='',
                                body=json.dumps(publication))
            print(" [x] Sent %r" % publication,)
            connection.close()
            return True
        except Exception as e:
            app.logger.error("Unexpected error:", sys.exc_info()[0])
            return False

    def documents_count(self):
        response = self.publications_repository.count()
        app.logger.info("response {0}".format(response))
        return response