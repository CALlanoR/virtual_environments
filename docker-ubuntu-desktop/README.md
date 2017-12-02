# Ubuntu Desktop Dockerfile

Docker container for Ubuntu 16.04 including ubuntu-desktop and vncserver.

# How to run

1. Create the docker image
sudo docker build -t ubuntu-desktop-16-04 .

2. Create the container
sudo docker run -di -p 127.0.0.1:5901:5901 --name=ubuntu-desktop ubuntu-desktop-16-04

and then connect to:

`vnc://<host>:5901` via VNC client (https://www.realvnc.com/en/connect/download/viewer/linux/).

The VNC password is `password`.


Notes:
1. run the Dropbox daemon from the newly created .dropbox-dist folder.
~/.dropbox-dist/dropboxd
