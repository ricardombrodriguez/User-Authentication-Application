FROM php:7.2.6-apache

RUN apt-get update -y && apt-get install -y curl && apt-get clean -y

RUN docker-php-ext-install mysqli

# flask:

FROM python:3.6

COPY . /var/www/html/

WORKDIR /var/www/html/

RUN pip3 install -r requirements.txt

EXPOSE 5000 

CMD ["python3", "server.py"]