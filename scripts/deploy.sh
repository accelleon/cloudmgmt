#!/bin/sh

randpass() {
  cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w $1 | head -n 1
}

# Ensure the script is run at the root level
[ "`id -u`" != 0 ] && echo "You must run this script as root." && exit 2

sudo apt update
sudo apt upgrade -y

# Grab postgresql 14 repo
echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" | sudo tee /etc/apt/sources.list.d/postgresql-pgdg.list &gt; /dev/null
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

# Python 3.9 repo
sudo add-apt-repository ppa:deadsnakes/ppa

# Npm repo (v14)
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -

# Pull in all our packages
sudo apt update
sudo apt install nodejs postgresql-14 redis nginx supervisor python3.9 python3.9-venv python3-pip -y

# install poetry
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3.9 -

# Build frontend
cd frontend
npm install
quasar build

# Copy the frontend over
mkdir -p /opt/cloudcost/public
cp -r dist/spa/* /opt/cloudcost/public

cd ..
# Copy our configuration files
cp -r ./conf/* /

# Copy the backend over
cd ../backend
cp -r . /opt/cloudcost
cd /opt/cloudcost/app

# Grab requirements via poetry
poetry install

# Generate various secrets
DBUSER=cloudcost
DBPASS=`randpass 16`
ADMIN_PASS=`randpass 16`
SECRET_KEY=`randpass 64`

# Create the database
sudo -u postgres psql -c "CREATE USER $DBUSER WITH PASSWORD '$DBPASS';"
sudo -u postgres psql -c "CREATE DATABASE cloudcost OWNER $DBUSER;"

# Generate our config file
cfg_cmd=$(cat << EOF
{
        "SERVER_NAME": "127.0.0.1",
        "SERVER_HOST": "https://127.0.0.1",
        "PROJECT_NAME": "app",

        "POSTGRES_SERVER": "localhost",
        "POSTGRES_USER": "$DBUSER",
        "POSTGRES_PASSWORD": "$DBPASS",
        "POSTGRES_DB": "cloudcost",

        "FIRST_USER_PASS": "$ADMIN_PASS",
        "SECRET_KEY": "$SECRET_KEY",
}
EOF
)

echo "$cfg_cmd" > /opt/cloudcost/config.json
if [[ $? -ne 0 ]]; then
  echo "Failed to generate config."
  exit 1
fi

# Initialize the database
/opt/cloudcost/app/.venv/bin/alembic upgrade head
/opt/cloudcost/app/.venv/bin/python -m app.init_data

# Hard link the nginx config
ln -s /opt/cloudcost/conf/sites-available/cloudcost /opt/cloudcost/conf/sites-enabled/cloudcost

# Generate SSL certs for nginx
mkdir -p /opt/cloudcost/conf/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /opt/cloudcost/conf/ssl/server.key -out /opt/cloudcost/conf/ssl/server.crt

# Users and permissions for everything
groupadd -r www-data
groupadd -r cloudcost

adduser --system --no-create-home --user-group --disabled-login --disabled-password nginx
adduser --system --no-create-home --user-group --disabled-login --disabled-password celery

usermod -a -g www-data nginx
usermod -a -g celery cloudcost

chown -R nginx:www-data /opt/cloudcost/nginx
chmod -R 0444 /opt/cloudcost/nginx
chgrp -R www-data /opt/cloudcost/public
chmod -R 0444 /opt/cloudcost/public

chgrp -R cloudcost /opt/cloudcost/app
chmod -R u-w /opt/cloudcost/app
chmod -R g-w /opt/cloudcost/app
chmod -R o-w /opt/cloudcost/app

chown -R nginx:www-data /var/log/supervisor/nginx*
chown -R celery:cloudcost /var/log/supervisor/celery*