FROM alpine:latest as builder

LABEL maintainer="Viste <viste@pprfnk.tech>"

RUN apk update \
  && apk add  --no-cache openssl ca-certificates \
  && update-ca-certificates \

RUN	apk update && apk add --no-cache git curl perl unzip gcc binutils build-base libgcc make \
    libxslt libxslt-dev libxml2 libxml2-dev pkgconf pkgconfig openssl openssl-dev ca-certificates pcre nasm yasm yasm-dev coreutils musl-dev \
    libc-dev pcre-dev zlib-dev lua-dev gd gd-dev geoip geoip-dev

# Set environment variables
ENV NGINX_RTMP_VERSION="1.2.2"
ENV RESTY_VERSION="1.21.4.3"

# Download and unpack sources
RUN cd /tmp && curl -fSL https://openresty.org/download/openresty-${RESTY_VERSION}.tar.gz | tar xz
RUN cd /tmp && curl -fSL https://github.com/arut/nginx-rtmp-module/archive/v${NGINX_RTMP_VERSION}.tar.gz | tar xz

# Build OpenResty with RTMP module
RUN cd /tmp/openresty-${RESTY_VERSION} \
    && ./configure --with-cc-opt="-I/usr/include" \
                   --with-ld-opt="-L/usr/lib" \
                   --add-module=/tmp/nginx-rtmp-module-${NGINX_RTMP_VERSION} \
                   --with-http_ssl_module \
                   --with-http_v2_module \
                   --with-http_mp4_module \
                   --with-http_flv_module \
                   --with-http_auth_request_module \
                   --with-http_geoip_module=dynamic \
                   --with-http_gunzip_module \
                   --with-http_gzip_static_module \
                   --with-http_image_filter_module=dynamic \
                   --with-http_stub_status_module \
                   --with-http_secure_link_module \
                   --with-http_sub_module \
                   --with-http_xslt_module=dynamic \
                   --with-stream \
                   --with-stream_ssl_module \
                   --with-mail \
                   --with-mail_ssl_module \
                   --with-http_realip_module \
    && make -j$(getconf _NPROCESSORS_ONLN) \
    && make install

# Final image
FROM alpine:latest

LABEL maintainer="Viste <viste@pprfnk.tech>"

# Copy OpenResty from builder stage
COPY --from=builder /usr/local/openresty /usr/local/openresty

# Install runtime dependencies
RUN apk add --no-cache \
    libgcc \
    libstdc++ \
    pcre \
    zlib \
    openssl \
    geoip \
    libxslt \
    gd \
    ffmpeg

# Set environment variables for Lua package paths
ENV PATH="/usr/local/openresty/bin:/usr/local/openresty/nginx/sbin:$PATH"
ENV LUA_PATH="/usr/local/openresty/site/lualib/?.lua;/usr/local/openresty/site/lualib/?/init.lua;/usr/local/openresty/lualib/?.lua;/usr/local/openresty/lualib/?/init.lua;./?.lua"
ENV LUA_CPATH="/usr/local/openresty/site/lualib/?.so;/usr/local/openresty/lualib/?.so;./?.so"

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
COPY rtmp/nginx.conf /usr/local/openresty/nginx/conf/nginx.conf

#RUN chown nginx:nginx -R /home

# Forward logs to Docker
RUN ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log \

# Copy nginx configuration files
COPY nginx.conf /usr/local/openresty/nginx/conf/nginx.conf

# Expose ports for HTTP and RTMP
EXPOSE 80 1935
STOPSIGNAL SIGTERM

# Start OpenResty (Nginx)
CMD ["/usr/local/openresty/bin/openresty", "-g", "daemon off;"]
