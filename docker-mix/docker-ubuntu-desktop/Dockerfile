FROM ubuntu:16.04
MAINTAINER Carlos Alberto Llano R.

ENV DEBIAN_FRONTEND noninteractive
ENV USER root

RUN add-apt-repository ppa:webupd8team/sublime-text-3

RUN apt-get update && \
    apt-get install -y --no-install-recommends ubuntu-desktop && \
    apt-get install -y gnome-panel gnome-settings-daemon metacity nautilus gnome-terminal && \
    apt-get install -y tightvncserver && \
    apt-get install -y mc vim terminator gimp  texlive-full shutter texmaker firefox wget && \
    apt-get install -y sublime-text-installer evince && \
    mkdir /root/.vnc

RUN wget -O - "https://www.dropbox.com/download?plat=lnx.x86_64" | tar xzf -

ADD xstartup /root/.vnc/xstartup
ADD passwd /root/.vnc/passwd

RUN chmod 600 /root/.vnc/passwd

CMD /usr/bin/vncserver :1 -geometry 1280x800 -depth 24 && tail -f /root/.vnc/*:1.log

EXPOSE 5901
