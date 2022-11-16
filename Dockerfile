FROM python:3.10
FROM ubuntu:22.04
WORKDIR .

RUN apt-get install -y gcc

ADD odbcinst.ini /etc/odbcinst.ini
RUN apt-get update
RUN apt-get install -y tdsodbc unixodbc-dev
RUN apt install unixodbc-bin -y
RUN apt-get clean -y


COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
ENTRYPOINT ["python"]
CMD ["main.py"]