FROM tiangolo/nginx-rtmp

RUN mkdir -p /var/sock
RUN mkdir -p /home/static
RUN mkdir -p /home/streams
RUN mkdir -p /home/streams/rec

EXPOSE 80
EXPOSE 1935
COPY rtmp/crossdomain.xml /home/static/crossdomain.xml
COPY rtmp/stat.xsl  /home/static/stat.xsl
COPY rtmp/nginx.conf /etc/nginx/nginx.conf