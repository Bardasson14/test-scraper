# syntax=docker/dockerfile:1

FROM ubuntu:22.04

COPY . /app
WORKDIR /app

# Instala as dependências
RUN apt-get update
RUN apt-get install git python3 -y
RUN echo $(python --version)

# Clona os repositórios
RUN mkdir /projects
RUN mkdir /projects/jenkins
RUN git clone https://github.com/jenkinsci/jenkins.git /projects/jenkins

VOLUME /projects

CMD python3 main.py