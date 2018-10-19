FROM centos:7
MAINTAINER Carlos Llano

# Tomcat and Java Vars
ENV JDK_MAJOR_VERSION=8u181 \
    JDK_VERSION=1.8.0_181 \
    TOMCAT_MAJOR_VERSION=8 \
    TOMCAT_VERSION=8.0.53 \
    JAVA_HOME=/opt/java \
    CATALINA_HOME=/opt/tomcat \
    PATH=$PATH:$JAVA_HOME/bin:${CATALINA_HOME}/bin:${CATALINA_HOME}/scripts \
    JAVA_OPTS="-Xms512m -Xmx2048m"

# Update and install latest packages and prerequisites
RUN yum -y update && yum clean all && yum -y install wget mc curl
RUN yum -y install sudo epel-release; yum clean all


# Install postgresql
RUN echo "Installing postgresql..." && \
    yum -y install postgresql-server postgresql postgresql-contrib supervisor pwgen; yum clean all

ADD ./postgresql-setup /usr/bin/postgresql-setup
ADD ./supervisord.conf /etc/supervisord.conf
ADD ./start_postgres.sh /start_postgres.sh

# Sudo requires a tty. fix that.
RUN sed -i 's/.*requiretty$/#Defaults requiretty/' /etc/sudoers
RUN chmod +x /usr/bin/postgresql-setup
RUN chmod +x /start_postgres.sh

RUN /usr/bin/postgresql-setup initdb
ADD ./postgresql.conf /var/lib/pgsql/data/postgresql.conf
RUN chown -v postgres.postgres /var/lib/pgsql/data/postgresql.conf
RUN echo "host    all             all             0.0.0.0/0               md5" >> /var/lib/pgsql/data/pg_hba.conf

VOLUME ["/var/lib/pgsql"]
EXPOSE 5432
CMD ["/bin/bash", "/start_postgres.sh"]

    
# Install Oracle JDK
RUN echo "Installing Java JDK..." && \
    cd /opt && \
    wget -nv --no-check-certificate --no-cookies --header "Cookie: oraclelicense=accept-securebackup-cookie" \
    http://download.oracle.com/otn-pub/java/jdk/${JDK_MAJOR_VERSION}-b13/96a7b8442fe848ef90c96a2fad6ed6d1/jdk-${JDK_MAJOR_VERSION}-linux-x64.tar.gz \
    -O /opt/jdk-${JDK_MAJOR_VERSION}-linux-x64.tar.gz && \
    tar -xzf /opt/jdk-${JDK_MAJOR_VERSION}-linux-x64.tar.gz && \
    rm /opt/jdk-${JDK_MAJOR_VERSION}-linux-x64.tar.gz && \
    mv /opt/jdk${JDK_VERSION} ${JAVA_HOME} && \
    ls /opt -la

# Install Tomcat
RUN echo "Installing Tomcat..." && \
    cd /opt && \
    wget -nv http://apache.mirror.gtcomm.net/tomcat/tomcat-${TOMCAT_MAJOR_VERSION}/v${TOMCAT_VERSION}/bin/apache-tomcat-${TOMCAT_VERSION}.tar.gz \
    -O /opt/apache-tomcat-${TOMCAT_VERSION}.tar.gz && \
    tar -xzf /opt/apache-tomcat-${TOMCAT_VERSION}.tar.gz && \
    rm /opt/apache-tomcat-${TOMCAT_VERSION}.tar.gz && \
    mv /opt/apache-tomcat-${TOMCAT_VERSION} ${CATALINA_HOME} && \
    ls /opt -la

# Tomcat scripts setup
COPY scripts/ ${CATALINA_HOME}/scripts/
RUN chmod +x ${CATALINA_HOME}/scripts/*.sh

# Expose and Start Services
WORKDIR ${CATALINA_HOME}
EXPOSE 8080 8009
CMD ["/opt/tomcat/scripts/tomcat.sh"]
