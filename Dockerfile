FROM python:3.10
FROM ubuntu:22.04
WORKDIR .

RUN apt-get update && apt-get install -y gnupg
RUN apt-get install -y curl
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list > /etc/apt/sources.list.d/mssql-release.list


RUN sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18
RUN sudo apt-get install -y unixodbc-dev


COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
ENTRYPOINT ["python"]
CMD ["main.py"]