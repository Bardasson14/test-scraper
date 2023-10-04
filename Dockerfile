# syntax=docker/dockerfile:1

FROM ubuntu:22.04

COPY . /app
WORKDIR /app

# Instala as dependências
RUN apt-get update
RUN apt-get install git python3 python3-pip -y
RUN apt-get install openjdk-17-jre-headless -y

# Configura ownership do git
RUN git config --global --add safe.directory /app

# Clona os repositórios (TODO: automatizar mkdirs e listagem de repos que serão clonados)
RUN mkdir /projects
RUN mkdir /projects/jenkins
RUN git clone https://github.com/jenkinsci/jenkins.git /projects/jenkins

VOLUME /projects

RUN chmod 777 /app/RefactoringMiner-2.4.0/bin/RefactoringMiner
CMD python3 main.py

# CMD tail -f