Building a distributed memcached environment is far simpler than you might have thought. The memcached daemon is blind about the cluster setup and has no special configuration on the server side to run the cluster, the client is actually doing the data distribution not the server.

How it works
============
What happens is that you specify a list of your servers to your client configuration and the client library uses consistent hashing to decide which server a certain key-value should go to.

The constructor of the client object here was fed with a couple of interesting parameters: 
binary = True: This is to configure pylibmc to use the memcached binary protocol not the ASCII protocol.
behaviors={"tcp_nodelay": True, "ketama": True}: This configures the memcached connection socket to use the tcp_nodelay socket option which disables Nagle's algorithm (http://en.wikipedia.org/wiki/Nagle%27s_algorithm) on the socket level. Setting "ketama" = True means that pylibmc is using md5 hashing and that it's using consistent hashing for key distribution.

After we have created the client object, we have set two keys ahmed and tek with the value Hello World and what actually happens behind the scenes is that each key-value pair is actually stored on a different daemon, according to the consistent hashing of the key.

You can checkout Redis at http://redis.io and Kyoto Tycoon at http://fallabs.com/kyototycoon/.

How access to machines
======================
vagrant ssh machine_name

Change default password for ubuntu user:
sudo passwd ubuntu

Links
=====
https://app.vagrantup.com/ubuntu/boxes/xenial64
http://kirang89.github.io/blog/2013/01/24/installing-pylibmc-in-ubuntu/
https://wincent.com/wiki/Testing_memcached_with_telnet

In php
======
If you are planning to connect to a cluster of memcached servers you will need to add all the servers using the addServer method:

<?php
/* OO API */
$memcache = new Memcache;
$memcache->addServer('memcached_host1', 11211);
$memcache->addServer('memcached_host2', 11211);
?>


In python
=========
http://sendapatch.se/projects/pylibmc/behaviors.html
ketama : True, means that pylibmc is using md5 hashing and that it's using consistent hashing for key distribution.
tcp_nodelay : True, which disables Nagle’s algorithm. https://es.wikipedia.org/wiki/Algoritmo_de_Nagle
remove_failed : 1, if set, a server will be removed from the server list after this many operations on it in a row have failed.
retry_timeout: 1, retry them once every minute.
dead_timeout: 60, Once a server has been marked dead, wait this amount of time (in seconds) before checking to see if the server is alive again.
