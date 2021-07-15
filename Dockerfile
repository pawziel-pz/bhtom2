FROM python:3.8-slim-buster

EXPOSE 8000

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

COPY ./requirements.txt /requirements.txt
COPY ./manage.py /manage.py
COPY ./bhtom2 /bhtom2

RUN pwd

RUN python -m pip install -r requirements.txt

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]