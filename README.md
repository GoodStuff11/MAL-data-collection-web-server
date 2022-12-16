# MAL Show Tracker Web Server

## Setup webserver locally

You first need to fill in `secrets.sh` in the code folder with a myanimelist api client token.

Then run `docker compose up -d`. Before doing this, you can modify the `docker-compose.yml` to write to a different location, since it's likely that the location that I have doesn't exist. Due to all the code used in the container being put there with a volume, you can modify the code and it will automatically be changed in the docker container. There is no need for the code to be built into the image since docker compose makes it easy enough to setup the project from a cloned repository. Then you can access the grafana ui under `http://localhost:3000` and the influxdb ui under `http://hostlocal:8086`.

First go to the influxdb ui, make a password and username and get an api token. Store this token in `secrets.sh`. This will allow for writing to and querying the database from grafana or elsewhere.

To setup grafana, login (your initial username and password is, admin admin respectively) and create a data source. Here you can find influxdb, insert the influxdb api token and under host, input `http://db:8086`.

## Running web server remotely

Having your computer running 24/7 isn't the only way to keep the server running. If some other computer is available (perferably linux so it's easier to setup) to act as a server, the web server can be implemented much more conviently.

The first step is to set everything up on the server, including cloning this repository there and getting the proper secrets there as well. Then you can run `docker compose up -d` and the web server will be running. You can access the services of your server on any computer in the local network by using the ip of the server (for example, calling `http://172.1.1.12:3000`, where in this case port 3000 would correspond to influxdb). It is also convenient to set this ip as a static ip address so it won't change.

It is also possible to communicate to the server in another network. In my case, I used ssh to communicate. The setup is as follows:

1. Install openssh-server on server
    - At this point you can call `ssh <user>@<server-ip>` to connect to the server while on the local network. 
    - When logging in you will be prompted for a password, and you will then be logged in. This is insecure since you are able to guess the password.
2. Configure the `/etc/ssh/sshd_config` (server settings) and `/etc/ssh/ssh_config` (client settings) to properly configure the ssh server. Here you will be able to remove passwords but DO NOT do this yet. However, you can customize many things here to make your server more secure.
3. In order to remove the need for passwords, you need to setup passwordless login, which involves setting up an ssh key pair. 
    - call `ssh-keygen`, and save the key pair to whatever file you want (id_rsa by default).
    - transfer the public key (with `.pub` extension) to the server. This can be done with ssh (since you can access with a password) by using a special command (`ssh-copy-id`) or doing it manually. You can also send the public key over by having another user which has ssh authentication do the above approach or by physically logging into the computer.
    - the public key will need to be put in `~/ssh/authorized_keys`
    - you will also need to setup a ssh client on the client computer.
    - If you did everything right, then attempting to login with ssh will not ask you for a password even when the password is enabled.
4. Configure the ssh server to not use passwords. This will make the ssh server much more secure.
5. Setup port forwarding using the router admin interface to forward some selected port to port 22 (corresponds to ssh) of the server's ip. This step should not be done before passwords are turned off so that there is no way for an intruder to login by guessing your password.
    - Now you can access the server from anywhere by using ssh. You can use the following command `ssh -p <port> <user>@<public-ip-of-server-network> -L 3000:<server-ip>:3000 -L 8086:<server-ip>:8086`
    - The `-L` in the command sets up port forwarding using ssh. This makes it so that you can access the interfaces on the remote computer using `localhost:3000` or `localhost:8086`. This port forwarding also means that you can query and add data to the influxdb database from outside the server if desired.
6. The public ip is able to change, but it's not easy to make the public ip static. However, you are able to track the public ip using a ddns. For example, you can use something like duckdns to convert the above command to the following: `ssh -p <port> <user>@<domain>.duckdns.org -L 3000:<server-ip>:3000 -L 8086:<server-ip>:8086`

## How it works

Running `docker compose up -d` will start up a cluster of three docker containers, an influxdb container used as the database, a grafana container used as a dashboard and a container to run a cron job that will periodically query the MAL api for data.

When the container queries the MAL api for data, it will use the influxdb cli (equivalent to the influxdb api, which can be called using curl POST) to write to the database. To do this, the container will make use of the network between docker containers, which docker compose makes very easy to access (`http://db:8086` for example, where the ip is substituted for the name of the container as specified in `docker-compose.yml`).
