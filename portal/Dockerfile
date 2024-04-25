FROM python:3

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get install -y nodejs
RUN apt-get install -y npm

COPY portal/server.js portal/package.json /app/
RUN npm install

COPY portal/ /app

EXPOSE 5000

CMD ["node", "server.js", "&"]
CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "8", "wsgi:app"]
