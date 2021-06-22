FROM python:3.8-slim

MAINTAINER Vladimir Prisyazhnikov <vprisyazhnikov@navicons.ru>

WORKDIR /opt/python_elastic_index_cleaner

COPY requirements.txt ./

RUN pip3 install --no-cache-dir --upgrade pip

RUN pip3 install --no-cache-dir -r requirements.txt

COPY app.py ./

ENV ELASTIC_HOST='https://your_elastic_host:9200'
ENV ELASTIC_USERNAME='your_elastic_username'
ENV ELASTIC_PASSWORD='your_elastic_password'
ENV AMOUNT_OF_DAYS='*-prod-*=30,*-test-*=15,*-stage-*=15,*-dev-*=15,*-stress-test-*=7,*-apm-*=3,*=30'

CMD [ "python", "app.py" ]
