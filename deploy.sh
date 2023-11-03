#!/usr/bin/env bash

OPTIONS_SHORT="t:s:"
OPTIONS_LONG="to:setting:,help"

PROJECT='common-task-system-client'
DEPLOY_TO="server"
SETTING=""


if ! ARGS=$(getopt -o $OPTIONS_SHORT --long $OPTIONS_LONG -n "$0" -- "$@"); then
  echo "Terminating..."
  echo -e "Usage: ./$SCRIPT_NAME [options]\n"
  exit 1
fi

eval set -- "${ARGS}"

while true;
do
    case $1 in
        -t|--to)
            echo "DEPLOY_TO: $2;"
            DEPLOY_TO=$2;
            shift 2
            ;;
        -s|--setting)
            echo "setting: $2;"
            SETTING=$2
            shift 2
            ;;
        --)
          shift 2
          break
          ;;
        ?)
          echo "there is unrecognized parameter."
          exit 1
          ;;
    esac
done


function deploy_to_pypi() {
  rm -rf ./dist/*
  python setup.py sdist
  twine upload dist/*

}

function deploy_to_docker() {
  echo "Deploying to docker..."
  docker build -t common-task-system-client .
  docker tag common-task-system-client cone387/common-task-system-client:latest
#  docker push cone387/common-task-system-client:latest
}



function deploy_to_server() {
  #   docker run -it --rm --name common-task-system-client cone387/common-task-system-client:latest
  if [ "$SETTING" != "" ];
  then
    if [ ! -f "$SETTING" ];
    then
      echo "SETTING<$SETTING> does not exist"
      exit 1
    fi
    server_path="/etc/$PROJECT/";
    if [ "$context" != "default" -a "$context" != "" ];
    then
      # docker context 为其它服务器, 先将配置文件拷贝到服务器上
      server=$(docker context inspect | grep -o 'Host.*' | sed 's/.*: "ssh:\/\/\(.*\)".*/\1/')
      echo "server is $server"
      if [ "$server" = "" ];
      then
        exit 1
      fi
      ssh server "mkdir -p $server_path"
      scp $SETTING $server:$server_path;
    else
      # docker context 为本地, 直接将配置文件拷贝到本地server_path
      echo "cp -f $SETTING $server_path"
      cp -f $SETTING $server_path
    fi
    VOLUME="-v $server_path:/home/$PROJECT/configs"
    ENV="-e TASK_CLIENT_SETTINGS_MODULE=configs.$(basename $SETTING .py)";
  fi
  echo "Deploying to server..."
  cid=`docker ps -a | grep $PROJECT | awk '{print $1}'`
  for c in $cid
    do
        docker stop $c
        docker rm $c
    done
  echo "docker build -t $PROJECT ."
  NOW=`date "+%Y%m%d%H%M%S"`
  docker build -t $PROJECT .
  echo ""
  name="$PROJECT-$NOW"
  docker run -d -v /var/run/docker.sock:/var/run/docker.sock $VOLUME $ENV --log-opt max-size=100m --name $name $PROJECT
}



if [ "$DEPLOY_TO" = 'pypi' ];
then
  deploy_to_pypi
elif [ "$DEPLOY_TO" = 'docker' ];
then
  deploy_to_docker
elif [ "$DEPLOY_TO" = 'server' ];
then
  deploy_to_server
else
  echo "Unknown deploy target: $DEPLOY_TO"
  exit 1
fi