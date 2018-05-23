Links
=====
https://www.howtoforge.com/setting-up-a-high-availability-load-balancer-with-haproxy-keepalived-on-debian-lenny

1. vagrant up
2. in your local web browser put: 192.168.56.99
	2.1 reload the page a lot of times
	2.2 put in your local web browser: http://192.168.56.99/haproxy?stats
		user1:password
	2.3 reload the page a lot of times and see the haproxy stats
	2.4 shutdown web1, reload the page again and see the haproxy stats
3. shutdown loadbalancer1
4. reload the page a lot of times