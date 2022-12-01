# MAL Show Tracker Web Server

## Setup webserver locally

You first need to fill in `secrets.sh` with a myanimelist api client token.

Then run `docker compose up -d`. Before doing this, you can modify the `docker-compose.yml` to write to a different location as needed, such as a hard drive. Then you can access the grafana ui under `http://localhost:3000` and the influxdb ui under `http://hostlocal:8086`.

First go to the influxdb ui, make a password and username and get an api token. Store this token in `secrets.sh`. This will allow for writing to and querying the database from grafana or elsewhere.

To setup grafana, login (your initial username and password is, admin admin respectively) and create a data source. Here you can find influxdb, insert the influxdb api token and under host, input `http://db:8086`.

## How it works

Running `docker compose up -d` will start up a cluster of three docker containers, an influxdb container used as the database, a grafana container used as a dashboard and a container to run a cron job that will periodically query the MAL api for data.

When the container queries the MAL api for data, it will use the influxdb cli (equivalent to the influxdb api, which can be called using curl POST) to write to the database. To do this, the container will make use of the network between docker containers, which docker compose makes very easy to access (`http://db:8086` for example, where the ip is substituted for the name of the container as specified in `docker-compose.yml`).