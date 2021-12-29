FROM python:3.8

COPY . /flask/

WORKDIR /flask/

RUN pip3 install -r requirements.txt

EXPOSE 5001

CMD ["flask","run","--host","172.2.0.3","--port","5001"]