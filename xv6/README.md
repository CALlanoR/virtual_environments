https://www.ics.uci.edu/~aburtsev/238P/2018fall/hw/xv6-setup.html

sudo docker pull grantbot/xv6

cd /home/callanor/xv6
git clone git://github.com/mit-pdos/xv6-public.git

sudo docker run -it -v /home/callanor/Documents/personal/virtual_environments/xv6:/xv6 grantbot/xv6:latest
sudo docker start <<name>>
sudo docker exec -ti <<name>> bash

sudo docker run -di --name=myxv6 -v /home/callanor/Documents/personal/virtual_environments/xv6:/xv6 grantbot/xv6:latest
sudo docker exec -ti myxv6 bash

cd cd xv6/xv6-public/

make qemu-nox

wait for the prompt

ls
cat README

to exit of xv6: Ctrl A X

https://medium.com/@harshalshree03/xv6-implementing-ps-nice-system-calls-and-priority-scheduling-b12fa10494e4