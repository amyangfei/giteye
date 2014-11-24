#!/bin/bash

if [ ! -f ./conf/nginx.conf ]; then
    echo "./conf/nginx.conf not found"
    exit 1
fi

if [ ! -f ./conf/giteye.conf ]; then
    echo "./conf/giteye.conf not found"
    exit 1
fi

cat > Dockerfile <<EOF
FROM nginx:1.7
# upgrade & install required packages

ENV HOMEDIR /home/giteye
RUN mkdir -p \${HOMEDIR}
RUN mkdir -p \${HOMEDIR}/var/log/nginx
RUN groupadd -r giteye && useradd -r -g giteye giteye -s /bin/bash -d \${HOMEDIR}
RUN echo 'giteye:giteye' | chpasswd

# copy nginx config file
ADD ./conf/nginx.conf /etc/nginx/nginx.conf
ADD ./conf/giteye.conf /etc/nginx/sites-enabled/giteye.conf

RUN chown -R giteye:giteye \${HOMEDIR}

EXPOSE 80

EOF

docker build --force-rm -t giteye/nginx . && rm -f Dockerfile

# sudo docker run --name "giteye-nginx" -h "giteye-nginx" -d -p 80:80 \
#    --link giteye-web:giteye-web giteye/nginx
