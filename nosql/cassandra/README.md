https://hub.docker.com/_/cassandra/
https://www.paradigmadigital.com/dev/cassandra-la-dama-de-las-bases-de-datos-nosql/
https://academy.datastax.com/resources/getting-started-apache-cassandra-and-python-part-i

1. Start a cassandra server
sudo docker run --name cassandradb_server -d cassandra

sudo docker exec -ti cassandradb_server bash
excute this command:(Cassandra Query Language Shell): cqlsh

First, we might wonder what is the equivalent of ‘show databases’ in SQL so we can create a database to get started if there is no default database. In Cassandra, or even in NOSQL world, they tend to avoid using the name database, like Mongo, HBase, so does Cassandra, they use something called keyspace.

The query language for Cassandra is extremely similar like SQL from MySQL.

cqlsh> DESC KEYSPACES;
cqlsh> create keyspace mykeyspace with replication = {'class':'SimpleStrategy', 'replication_factor':3} and durable_writes=true;
cqlsh> desc keyspaces;
cqlsh> use mykeyspace;
cqlsh:mykeyspace> desc keyspace mykeyspace;
cqlsh:mykeyspace> desc tables;
cqlsh:mykeyspace> create table mytable(firstname varchar, lastname varchar, ssn int primary key);
cqlsh:mykeyspace> desc tables;
cqlsh:mykeyspace> desc table mytable;

CREATE TABLE mykeyspace.mytable (
    ssn int PRIMARY KEY,
    firstname text,
    lastname text
) WITH bloom_filter_fp_chance = 0.01
    AND caching = {'keys': 'ALL', 'rows_per_partition': 'NONE'}
    AND comment = ''
    AND compaction = {'class': 'org.apache.cassandra.db.compaction.SizeTieredCompactionStrategy', 'max_threshold': '32', 'min_threshold': '4'}
    AND compression = {'chunk_length_in_kb': '64', 'class': 'org.apache.cassandra.io.compress.LZ4Compressor'}
    AND crc_check_chance = 1.0
    AND dclocal_read_repair_chance = 0.1
    AND default_time_to_live = 0
    AND gc_grace_seconds = 864000
    AND max_index_interval = 2048
    AND memtable_flush_period_in_ms = 0
    AND min_index_interval = 128
    AND read_repair_chance = 0.0
    AND speculative_retry = '99PERCENTILE';

cqlsh:mykeyspace>

As you can see, this is basically SQL and you can do create table, insert, update and delete as you have done in SQL… Here is another screen shot of some CRUD (create, read, update and delete.) operations I did.

cqlsh:mykeyspace> insert into mytable (firstname, lastname, ssn) values ('F1', 'L1', 1);
cqlsh:mykeyspace> insert into mytable (firstname, lastname, ssn) values ('F2', 'L2', 2);
cqlsh:mykeyspace> insert into mytable (firstname, lastname, ssn) values ('F3', 'L3', 3);
cqlsh:mykeyspace> insert into mytable (firstname, lastname, ssn) values ('F1', 'L11', 1);

cqlsh:mykeyspace> select * from mytable;


2. In another terminal connect to it from an application
sudo docker run -itd --name cassandra_client --link cassandradb_server ubuntu:14.04 /bin/bash

sudo docker exec -ti cassandra_client bash

3.1 Install curl
apt-get update
apt-get install -y curl vim nano

3.2 Install pip to download the cassandradb python library
curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
python3 get-pip.py

pip install cassandra-driver

3.3 mkdir /home/workdir
3.4 cd /home/workdir
3.5 Copy cassandra_test.py to /home/workdir
3.6 python cassandra_test.py
