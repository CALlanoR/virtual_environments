FROM ubuntu:16.04
MAINTAINER Carlos Llano <carlos_llano@hotmail.com>

################################################################################
# Install requirements: git, jq, openssh-server
################################################################################
RUN apt-get update && apt-get -y install git jq curl openssh-server sudo

################################################################################
# Install nginx
################################################################################
COPY nginx.sh /tmp/
RUN ["sh", "/tmp/nginx.sh"]

################################################################################
# Configurate guest user
################################################################################
RUN mkdir /var/run/sshd

# Add user guest to the image
RUN useradd -s /bin/bash -m guest
RUN echo "guest:guest" | chpasswd
RUN echo "guest ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

RUN sed -i "s/PermitRootLogin without-password/PermitRootLogin yes/" /etc/ssh/sshd_config

# SSH login fix. Otherwise user is kicked off after login
RUN sed "s@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g" -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]

################################################################################
# Install supervisor
################################################################################
#RUN apt-get install -y supervisor
#RUN mkdir -p /var/log/supervisor
#COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

#CMD /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf