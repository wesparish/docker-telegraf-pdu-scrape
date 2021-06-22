FROM telegraf:1.18

RUN apt-get update && \
    apt-get install python3-pip git python3 vim-tiny curl -y && \
    apt-get autoremove -y && \
    apt-get clean

ADD pdu-scrape/requirements.txt /
RUN pip3 install -r requirements.txt

ENV LOG_LEVEL="WARN" LC_ALL=C.UTF-8 LANG=C.UTF-8

COPY pdu-scrape/pdu-scrape.py /pdu-scrape.py
RUN chown root:root pdu-scrape.py

RUN mkdir /root/.ssh &&\
    chmod 700 /root/.ssh
COPY pdu-scrape/ssh/config /root/.ssh/config
RUN chmod 400 /root/.ssh/config

ENV PDU_SCRAPE_HOSTS=10.2.1.18,10.2.1.102
