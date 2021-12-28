FROM python:3.6

COPY ../requirements.txt /var/www/html/requirements.txt

COPY ../server.py /var/www/html/server.py

WORKDIR /var/www/html/

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python3", "server.py"]