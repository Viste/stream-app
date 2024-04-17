FROM python:3

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY portal/ /app
EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "8", "wsgi:app"]
