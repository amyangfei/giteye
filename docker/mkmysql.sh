#!/bin/bash

if [ ! -f ./conf/my.cnf ]; then
    echo "my.cnf not found"
    exit 1
fi

if [ ! -f ../deploy/giteye_dump.sql ]; then
    echo "../deploy/giteye_dump.sql not found"
    exit 1
fi

cd .. || exit $?

docker rmi giteye/mysql

cat > Dockerfile <<EOF
FROM mysql:5.5

ENV CNFDIR /etc/mysql
RUN mkdir -p \${CNFDIR}
RUN mkdir -p \${CNFDIR}/conf.d/
ADD ./docker/conf/my.cnf \${CNFDIR}/my.cnf
RUN chown -R mysql:mysql \${CNFDIR}

ENV HOMEDIR /home/giteye
RUN mkdir -p \${HOMEDIR}
RUN groupadd -r giteye && useradd -r -g giteye giteye -s /bin/bash -d \${HOMEDIR}
RUN echo 'giteye:giteye' | chpasswd
ADD ./deploy/giteye_dump.sql \${HOMEDIR}/giteye_dump.sql

EOF

docker build --force-rm -t giteye/mysql . && rm -f Dockerfile

# start a container
# sudo docker run --name "giteye-mysql" -h "giteye-mysql" -d -p 3006:3306 \
#    -e MYSQL_ROOT_PASSWORD=root -e MYSQL_USER=giteye -e MYSQL_PASSWORD=giteye -e MYSQL_DATABASE=giteye giteye/mysql

# connect to mysql
# sudo docker run -it --link giteye-mysql:giteye-mysql --rm mysql sh -c 'exec mysql -hgiteye-mysql -P3306 -uroot -p'

# import database structure
# mysql -u giteye -p --database=giteye < giteye_dump.sql
