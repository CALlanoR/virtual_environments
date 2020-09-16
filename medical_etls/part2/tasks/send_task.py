#!/usr/bin/env python
import pika
import uuid
import json
import os
import sys
import mysql.connector
import configparser
import logging.config
from datetime import datetime
from uuid import UUID

def _get_logger():
    logger = logging.getLogger(__name__)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    dir_name, filename = os.path.split(os.path.abspath(__file__))
    output_file = dir_name + "/vocabulary_etl.log"
    handler = logging.FileHandler(output_file)
    handler.setFormatter(formatter)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger

logger = _get_logger()

def uuid_convert(o):
    if isinstance(o, UUID):
        return o.hex

def send_task(task):
    config = configparser.ConfigParser()
    config.read('config.ini')
    database_configuration = config['rabbitmq']

    credentials = pika.PlainCredentials(database_configuration['user'],
                                        database_configuration['password'])
    connection = pika.BlockingConnection(pika.ConnectionParameters(
                                            database_configuration['host'],
                                            5672,
                                            '/',
                                            credentials))
    channel = connection.channel()

    channel.queue_declare(queue=database_configuration['queue'])

    channel.basic_publish(
        exchange='',
        routing_key=database_configuration['queue'],
        body=json.dumps(task, indent=4, default=uuid_convert),
        properties=pika.BasicProperties(
            delivery_mode = 2, # make message persistent
        )
    )
    print(" [x] Sent task: {}".format(task))
    connection.close()

def register_task(task):
    config = configparser.ConfigParser()
    config.read('config.ini')
    database_configuration = config['database']

    config = {
        'user': database_configuration['db_user'],
        'password': database_configuration['db_password'],
        'host': database_configuration['db_host'],
        'database': database_configuration['db_schema'],
        'raise_on_warnings': True
    }

    logger.info("Connecting to database...")
    cnx = mysql.connector.connect(**config)
    logger.info("The connection to the database was succesfull")

    now = datetime.now()
    sql = ("""INSERT INTO tasks(uuid, type, status, file_id, date, last_update_date)
              VALUES(%s, %s, %s, %s, %s, NULL)""")
    values = (
        str(task['uuid']),
        task['document_type'],
        "Pending",
        task['file_id'],
        now.strftime("%Y-%m-%d %H:%M:%S"), ## dd/mm/YY H:M:S
    )
    cursor = cnx.cursor()
    cursor.execute(sql, values)
    cnx.commit()
    logger.info("the task was registered with the id {}".format(cursor.lastrowid))
    cnx.close()

def main(file_id, document_type):
    task = {
        'uuid': uuid.uuid1().hex, # make a UUID based on the host ID and current time
        'file_id': file_id,
        'document_type': document_type
    }

    send_task(task)
    register_task(task)

if __name__ == "__main__":
    import sys
    if len(sys.argv) is not 3:
        print("Usage: python send_task.py drive_file_id document_type")
    else:
        # Take Id from shareable link
        file_id = sys.argv[1]
        # Types: vocabulary, concepts
        document_type = sys.argv[2]
        main(file_id, document_type)