FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]





#FROM python:3.12-slim
#
#WORKDIR /app
#
#ENV PYTHONDONTWRITEBYTECODE=1
#ENV PYTHONUNBUFFERED=1
#
#COPY requirements.txt .
#
#RUN pip install --no-cache-dir -r requirements.txt
#
#COPY . .
#
#RUN mkdir -p /app/logs
#
#CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]





##FROM python:3.14
##
##WORKDIR /app
##
##COPY requirements.txt .
##
##RUN pip install --no-cache-dir -r requirements.txt
##
##COPY . .
##
##ENV PYTHONDONTWRITEBYTECODE=1
##ENV PYTHONUNBUFFERED=1
##
##CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]