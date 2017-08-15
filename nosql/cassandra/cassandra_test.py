#!/usr/bin/python
# here is how you set up Cassandra on your local machine.
recordNumber = 100000

from cassandra.cluster import  Cluster
from cassandra.query import SimpleStatement

KEYSPACE = "mykeyspace"
def main():
    cluster = Cluster(['cassandradb_server'])
    session = cluster.connect()
    session.set_keyspace(KEYSPACE)

    future = session.execute_async("SELECT * FROM mytable")

    print("key\tcol1\tcol2")
    print("---\t----\t----")

    try:
        rows = future.result()
    except Exception as e:
        print(e.value)

    for row in rows:
        print(str(row))

main()
print('finished')
