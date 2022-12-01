FROM python:latest
WORKDIR /home
RUN wget -q https://repos.influxdata.com/influxdb.key && \
    echo '23a1c8836f0afc5ed24e0486339d7cc8f6790b83886c4c96995b88a061c5bb5d influxdb.key' | sha256sum -c && cat influxdb.key | gpg --dearmor | tee /etc/apt/trusted.gpg.d/influxdb.gpg > /dev/null && \
    echo 'deb [signed-by=/etc/apt/trusted.gpg.d/influxdb.gpg] https://repos.influxdata.com/debian stable main' | tee /etc/apt/sources.list.d/influxdata.list && \
    apt-get update -y && apt-get install influxdb2 -y

COPY read.py get_data.sh requirements.txt /home/
RUN pip install -r /home/requirements.txt
RUN influx config create --config-name influx-config --active --org personal --host-url http://db:8086
RUN apt-get install cron -y && \
    printf "SHELL=/bin/sh\nPATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin\n0 * * * * /home/get_data.sh >> /tmp/log 2>&1\n" | crontab -
CMD ["cron", "-f"]