FROM python:3

MAINTAINER Vladimir Prisyazhnikov <vprisyazhnikov@navicons.ru>

WORKDIR /opt/python_elastic_index_cleaner

RUN python -m pip install --upgrade pip

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./

ENV ELASTIC_HOST='https://your_elastic_host:9200'
ENV ELASTIC_USERNAME='your_elastic_username'
ENV ELASTIC_PASSWORD='your_elastic_password'
ENV AMOUNT_OF_DAYS='*-prod-*=30,*-test-*=11, *-stage-*=11,*-stress-test-*=5,*-demo-*=11, *=30'

CMD [ "python", "app.py" ]
