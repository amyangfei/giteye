#!/bin/bash

cd .. || exit $?

if [ ! -f requirements.txt ]; then
    echo "requirments.txt not found"
    exit 1
fi

cat > Dockerfile <<EOF
FROM python:2.7-onbuild
# upgrade & install required packages
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y git

ENV HOMEDIR /home/giteye
RUN mkdir -p \${HOMEDIR}
RUN groupadd -r giteye && useradd -r -g giteye giteye -s /bin/bash -d \${HOMEDIR}
RUN echo 'giteye:giteye' | chpasswd

# git clone giteye and copy config file
WORKDIR \${HOMEDIR}
RUN git clone https://github.com/amyangfei/giteye.git
WORKDIR \${HOMEDIR}/giteye/src
RUN cp config.py.template config.py
RUN chown -R giteye:giteye \${HOMEDIR}

EXPOSE 9999

CMD [ "cd", "\${HOMEDIR}/giteye/src" ]
CMD [ "python", "./application.py" ]

EOF

docker build --force-rm -t giteye/web . && rm -f Dockerfile

# sudo docker run --name "giteye-web" -h "giteye-web" -d -p 9999:9999 \
#    --link giteye-mysql:giteye-mysql --link giteye-redis:giteye-redis giteye/web
