FROM php:7.2.6-apache

RUN apt-get update -y && apt-get install -y curl && apt-get clean -y

RUN docker-php-ext-install mysqli