#!/bin/bash

if [ -f ./conf/redis.conf ]
then
    sudo docker run --name "giteye-redis" -h "giteye-redis" -d -p 6079:6379 -v ./conf/redis.conf::/usr/local/etc/redis/redis.conf redis /usr/local/etc/redis/redis.conf
else
    sudo docker run --name "giteye-redis" -h "giteye-redis" -d -p 6079:6379 redis
fi
