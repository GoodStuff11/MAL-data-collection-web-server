# MAL Show Tracker Web Server

## Setup webserver locally

You first need to fill in `secrets.sh` in the code folder with a myanimelist api client token.

Then run `docker compose up -d`. Before doing this, you can modify the `docker-compose.yml` to write to a different location, since it's likely that the location that I have doesn't exist. Due to all the code used in the container being put there with a volume, you can modify the code and it will automatically be changed in the docker container. There is no need for the code to be built into the image since docker compose makes it easy enough to setup the project from a cloned repository. Then you can access the grafana ui under `http://localhost:3000` and the influxdb ui under `http://hostlocal:8086`.

First go to the influxdb ui, make a password and username and get an api token. Store this token in `secrets.sh`. This will allow for writing to and querying the database from grafana or elsewhere.

To setup grafana, login (your initial username and password is, admin admin respectively) and create a data source. Here you can find influxdb, insert the influxdb api token and under host, input `http://db:8086`.

## Running web server remotely

It is not required that the web server be run on your computer, requiring that your computer always be running. If some other computer is available (perferably linux so it's easier to setup) to act as a server, the web server can be implemented much more conviently.

The first step is to set everything up on the server, including cloning this repository there and getting the proper secrets there as well. Then you can run `docker compose up -d` and the web server will be running. You can access the services on any computer in the local network by using the ip of the server (such as calling `http://172.1.1.12:3000`). It is also convenient to set this ip as a static ip address so it won't change if something goes wrong. 

It is also possible to communicate to the server in another network. There are multiple ways of doing this

1. Using SSH
    1. Install OpenSSH server on the server
    2. Give the server a static ip address (optional but convenient)
    3. Setup the proper port fowarding to allow ssh
2. Use VPN server to make VPN tunnel (I think also requires port forwarding)
3. Setup port forwarding directly to grafana and influxdb (rather unsafe, so make sure your password is good)
4. Using [tor](https://www.home-assistant.io/blog/2017/11/12/tor/)

## How it works

Running `docker compose up -d` will start up a cluster of three docker containers, an influxdb container used as the database, a grafana container used as a dashboard and a container to run a cron job that will periodically query the MAL api for data.

When the container queries the MAL api for data, it will use the influxdb cli (equivalent to the influxdb api, which can be called using curl POST) to write to the database. To do this, the container will make use of the network between docker containers, which docker compose makes very easy to access (`http://db:8086` for example, where the ip is substituted for the name of the container as specified in `docker-compose.yml`).
