FROM python:2.7-wheezy
RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    libxml2-dev libxslt-dev less

RUN pip install netlib configargparse pillow 
RUN pip install mitmproxy
ENV PYTHONPATH=/usr/app/src
COPY mitmproxy /usr/app/mitmproxy

EXPOSE 8080
CD /usr/app
CMD ["bash", "-i"]
