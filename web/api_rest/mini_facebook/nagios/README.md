
##  Every time you modify your configuration files, you should run a sanity check on them. It is important to do this before you (re)start Nagios, as Nagios will shut down if your configuration contains errors. In order to verify your configuration, run Nagios with the -v command line option like so: 
/opt/nagios/bin/nagios -v /opt/nagios/etc/nagios.cfg

## Nagios check_http Plugin Examples for HTTP / HTTPS
https://linux.101hacks.com/unix/check-http/

https://medium.com/@vishnuteja/nagios-core-check-disk-space-usage-on-a-remote-machine-using-nrpe-86cd2a8971c4