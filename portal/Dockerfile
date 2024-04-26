FROM python:3

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
RUN apt-get install -y nodejs
RUN node --version
RUN npm --version
COPY portal/server.js portal/package.json /app/
RUN npm install

COPY portal/ /app
COPY portal/start.sh /app/start.sh
RUN chmod +x /start.sh

EXPOSE 5000
EXPOSE 1207

# Запуск скрипта
CMD ["/app/start.sh"]
