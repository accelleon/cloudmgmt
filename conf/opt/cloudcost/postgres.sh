#!/bin/bash
stop_database() {
  sudo -u postgres /usr/bin/pg_ctlcluster --force 14 main stop
}

trap stop_database SIGKILL SIGINT SIGTERM SIGSTOP SIGHUP

pg_14_tmp=/var/run/postgresql/14-main.pg_stat_tmp
if [ ! -d "$pg_14_tmp" ]; then
  echo "folder $pg_14_tmp is missing. Creating now..."
  mkdir -p "$pg_14_tmp"
  echo "Done."
fi

sudo chown -R postgres.postgres "/var/run/postgresql/"

sudo -u postgres /usr/lib/postgresql/14/bin/postgres \
  -D /var/lib/postgresql/14/main \
  -c config_file=/etc/postgresql/14/main/postgresql.conf &

while [ 1 ]; do
  sleep 1
done