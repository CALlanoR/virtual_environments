in shell run osqueryi, and then run this query:
osquery> select path from osquery_extensions;

echo "SELECT * FROM etc_hosts;" | osqueryi
echo  "SELECT u.username, g.groupname FROM users as u JOIN groups as g ON u.gid = g.gid LIMIT 10;" | osqueryi
echo "SELECT * FROM apt_sources;" | osqueryi
echo "SELECT * FROM listening_ports;" | osqueryi
echo "SELECT * FROM users;" | osqueryi
echo "SELECT * FROM groups;" | osqueryi
echo "SELECT * FROM crontab;" | osqueryi
echo "SELECT * from processes;" | osqueryi
echo "SELECT * FROM time;" | osqueryi
echo "SELECT DISTINCT process.name, process.pid FROM processes AS process;" | osqueryi
echo "SELECT * from shell_history;" | osqueryi
echo "SELECT name, path, pid FROM processes;" | osqueryi
echo "select distinct user from logged_in_users;" | osqueryi
echo "select username,key from users join known_hosts using (uid);;" | osqueryi
echo "select username,key from users join known_hosts using (uid) group by username;" | osqueryi


mac
echo "select name,path from kernel_extensions where name not like 'com.apple%';" | osqueryi
echo "SELECT uid, name FROM listening_ports l, processes p WHERE l.pid=p.pid;" | osqueryi
echo "select key, subkey, value from preferences where path = '/Library/Preferences/com.apple.loginwindow.plist';" | osqueryi
echo "SELECT * FROM startup_items;" | osqueryi
echo "SELECT path, label, program_arguments, inetd_compatibility, root_directory FROM launchd;" | osqueryi
echo "select name, program || program_arguments AS executable from launchd where (run_at_load - 'true' AND keep_alive = 'true') and (program != '' or program_arguments !='') and executable like '/System/%';" | osqueryi
echo "select name, program || program_arguments AS executable from launchd;" | osqueryi --json
echo "select address,mac,count(mac) as mac_count from arp_cache group by mac having count(mac) > 0;" | osqueryi --json
echo "select key, subkey, value from preferences where path = '/Library/Preferences/com.apple.loginwindow.plist';" | osqueryi
echo "select * from apps where bundle_identifier = 'com.ht.RCSMac' or bundle_package_type like 'OSAX';" | osqueryi
echo "select * from launchd where path like '%com.apple.launchport.plist';" | osqueryi
echo "select * from wifi_networks;" | osqueryi
echo "select distinct pid, family, protocol, local_address, local_port, remote_address, remote_port, path from process_open_sockets where path <> '' or remote_address <> '';" | osqueryi
echo "select * from process_envs;" | osqueryi


sudo cp /usr/share/osquery/osquery.example.conf /etc/osquery/osquery.conf
cat /etc/osquery/osquery.conf 
sudo service osqueryd restart
ls -l /var/log/osquery/


$ sudo cp /var/osquery/osquery.example.conf /var/osquery/osquery.conf
$ sudo cp /var/osquery/com.facebook.osqueryd.plist /Library/LaunchDaemons/
$ sudo launchctl load /Library/LaunchDaemons/com.facebook.osqueryd.plist

$sudo osquery/tools/deployment/osqueryctl start
$sudo osquery/tools/deployment/osqueryctl stop
$sudo osquery/tools/deployment/osqueryctl status


/private/var/osquery/com.facebook.osqueryd.plist
/private/var/osquery/osquery.example.conf
/private/var/log/osquery/
/private/var/osquery/packs/{*}.conf
/usr/local/lib/osquery/
/usr/local/bin/osqueryctl
/usr/local/bin/osqueryd
/usr/local/bin/osqueryi