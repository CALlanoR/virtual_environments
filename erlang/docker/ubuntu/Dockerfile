FROM ubuntu:16.04
MAINTAINER Carlos Llano <carlos_llano@hotmail.com>

################################################################################
# Install requirements: git, jq, openssh-server
################################################################################
RUN apt-get update && apt-get -y install git jq curl openssh-server sudo

################################################################################
# Install erlang
################################################################################
ENV PATH=/opt/erlang/bin:/opt/rebar/bin:$PATH
ADD sources.list /etc/apt/sources.list
COPY erlang.sh /tmp/
RUN ["sh", "/tmp/erlang.sh"]
