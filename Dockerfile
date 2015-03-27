FROM cnry/python:2.7

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    libxml2-dev libxslt-dev less  net-tools vim-nox \
    mongodb

VOLUME /var/lib/mongodb/

RUN echo 'smallfiles=true' >> /etc/mongodb.conf; sed -ibkp 's/bind_ip.*/bind_ip = 0.0.0.0/' /etc/mongodb.conf 

# move
RUN apt-get install -y --no-install-recommends libffi-dev libssl-dev

RUN pip install netlib configargparse pillow pymongo mitmproxy ipython
ENV PYTHONPATH /usr/app/src
COPY mitmproxy /usr/app/mitmproxy

EXPOSE 8080 27017

WORKDIR /usr/app

CMD ["bash", "-i"]
