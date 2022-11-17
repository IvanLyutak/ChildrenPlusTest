FROM ubuntu:22.04
WORKDIR .

RUN apt update -y  &&  apt upgrade -y && apt-get update
RUN apt install -y curl python3.10 git python3-pip openjdk-8-jdk unixodbc-dev

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y --allow-unauthenticated msodbcsql18
RUN ACCEPT_EULA=Y apt-get install -y --allow-unauthenticated mssql-tools
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["python3"]
CMD ["main.py"]