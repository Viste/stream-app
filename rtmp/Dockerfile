FROM tiangolo/nginx-rtmp

# for future security now we can use root nah
#RUN groupadd --system --gid 101 nginx && useradd --system --gid nginx --no-create-home --home /nonexistent --comment "nginx user" --shell /bin/false --uid 101 nginx

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
COPY rtmp/nclients.xsl /home/static/nclients.xsl
COPY rtmp/nginx.conf /etc/nginx/nginx.conf

#RUN chown nginx:nginx -R /home

EXPOSE 80
EXPOSE 1935
