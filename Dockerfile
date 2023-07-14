FROM ubuntu:22.04

MAINTAINER cone

ENV TZ=Asia/Shanghai
ENV LANG zh_CN.UTF-8
ENV PROJECT_DIR /home/admin/task-system-client

# 1. 安装Python3.11
RUN apt-get update -y
RUN apt-get install -y python3.11
# 重命名python3.11为python3, pip3.11为pip3
RUN mv /usr/bin/python3.11 /usr/bin/python

RUN apt-get install curl -y
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python get-pip.py

COPY . $PROJECT_DIR

WORKDIR $PROJECT_DIR

## 2. 安装依赖
#RUN pip install common-task-system-client

RUN python setup.py build
RUN python setup.py install

RUN pip config --global set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install py-cone>=1.0.8
RUN pip install requests
RUN pip install PyMySQL>=1.0.2
RUN pip install redis
RUN pip install DBUtils
