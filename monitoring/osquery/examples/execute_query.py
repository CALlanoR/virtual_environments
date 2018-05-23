import osquery

if __name__ == "__main__":
    # Spawn an osquery process using an ephemeral extension socket.
    instance = osquery.SpawnInstance()
    instance.open()  # This may raise an exception

    # Issues queries and call osquery Thrift APIs.
    response = instance.client.query("select timestamp from time")
    print response
    response = instance.client.query(" select * from cpu_time")
    print response