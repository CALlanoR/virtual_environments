#!/usr/bin/env bash
OTP_VERSION=19.1.2

useradd -s /bin/bash -m callanor
echo "callanor:callanor" | chpasswd
echo "callanor ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

sed -i "s/PermitRootLogin without-password/PermitRootLogin yes/" /etc/ssh/sshd_config

# SSH login fix. Otherwise user is kicked off after login
sed "s@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g" -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
echo "export VISIBLE=now" >> /etc/profile

apt-get update \
  && apt-get install -y \
         autoconf \
         git \
         jq \
         openssh-server \
         build-essential \
         curl \
         libssl-dev \
         ncurses-dev \
  && apt-get clean \
  && rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*

cd /usr/local/src \
  && git clone -b OTP-${OTP_VERSION} https://github.com/erlang/otp.git \
  && cd /usr/local/src/otp \
  && ./otp_build autoconf \
  && ./configure --prefix=/opt/erlang-${OTP_VERSION} \
                 --enable-kernel-poll \
                 --enable-hipe \
                 --enable-dirty-schedulers \
                 --enable-smp-support \
                 --enable-m64-build \
                 --enable-sharing-preserving \
                 --without-javac \
                 --disable-vm-probes \
                 --disable-megaco-flex-scanner-lineno \
                 --disable-megaco-reentrant-flex-scanner \
  && make \
  && make install \
  && cd .. \
  && rm -rf otp_src_${OTP_VERSION}

echo "PATH=/opt/erlang-${OTP_VERSION}/bin:$PATH" >> /etc/environment

apt-get clean
apt-get autoremove