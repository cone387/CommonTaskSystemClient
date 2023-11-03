FROM ubuntu:22.04

MAINTAINER cone

ENV TZ=Asia/Shanghai
ENV LANG zh_CN.UTF-8
ENV PROJECT_DIR /home/admin/
ENV PROJECT_NAME task-system-client

# 1. 安装Python3.11
RUN apt-get update -y
RUN apt-get install -y python3.11
# 重命名python3.11为python3, pip3.11为pip3
RUN mv /usr/bin/python3.11 /usr/bin/python

RUN apt-get install curl -y
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python get-pip.py

WORKDIR $PROJECT_DIR/$PROJECT_NAME

COPY . $PROJECT_DIR/$PROJECT_NAME

## 2. 安装依赖
#RUN pip install common-task-system-client

RUN pip config --global set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install -r requirements.txt

RUN python setup.py install

# 这里需要返回到上级目录，如果在task-system-client目录下，会导致后面的task_system_client是从该目录下查找引起异常
WORKDIR $PROJECT_DIR
