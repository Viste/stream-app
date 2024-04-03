FROM tiangolo/nginx-rtmp

RUN mkdir -p /var/sock
RUN mkdir -p /home/streams
RUN mkdir -p /home/streams/rec

EXPOSE 8080
EXPOSE 1935

COPY rtmp/nginx.conf /etc/nginx/nginx.conf