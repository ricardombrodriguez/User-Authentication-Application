FROM php:7.2.6-apache

RUN apt-get update -y && apt-get install -y curl && apt-get clean -y

RUN docker-php-ext-install mysqli

# flask:

FROM python:3.6

COPY . /uap/src/

WORKDIR /uap/src/

RUN pip install -r requirements.txt

EXPOSE 5001 

CMD ["python3", "uap.py"]