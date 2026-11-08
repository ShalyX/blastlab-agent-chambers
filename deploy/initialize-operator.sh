#!/bin/sh
set -eu
umask 077
mkdir -p /etc/blastlab
if [ ! -s /etc/blastlab/operator.token ]; then
  openssl rand -hex 32 > /etc/blastlab/operator.token
fi
chmod 600 /etc/blastlab/operator.token
test -s /etc/blastlab/operator.token
printf 'OPERATOR_ACCESS_READY\n'
