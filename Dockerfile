FROM python:3

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

RUN npm install

COPY . /app
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 5000
EXPOSE 1207

# Запуск скрипта
CMD ["/app/start.sh"]
