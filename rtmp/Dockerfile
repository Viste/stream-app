FROM tiangolo/nginx-rtmp

RUN mkdir -p /var/sock
RUN mkdir -p /home/static
RUN mkdir -p /home/streams
RUN mkdir -p /home/storage

RUN apt-get update
RUN apt-get install -y jq

COPY rtmp/utils/start_stream.sh /home/start_stream.sh
COPY rtmp/utils/end_stream.sh  /home/end_stream.sh

RUN chmod +x /home/start_stream.sh
RUN chmod +x /home/end_stream.sh

COPY rtmp/crossdomain.xml /home/static/crossdomain.xml
COPY rtmp/stat.xsl  /home/static/stat.xsl
COPY rtmp/nsclients.xsl /home/static/nsclients.xsl
COPY rtmp/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
EXPOSE 1935
