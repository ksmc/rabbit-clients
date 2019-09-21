#!/usr/bin/env bash

NO_DOCKER=$1

echo "Preparing environment.  This may take a minute..."

python3 -m venv rabbittest > tests.log
source rabbittest/bin/activate >> tests.log
pip install -r requirements.txt >> tests.log
export RABBIT_URL=localhost

if [ -z "$NO_DOCKER" ]
then
  docker pull rabbitmq >> tests.log
  docker run -p 5672:5672 --name rabbitmq rabbitmq >> tests.log &
  sleep 30
  export DOCKER_STATUS='UP'
else
  export DOCKER_STATUS='DOWN'
fi

pytest --cov=rabbit_clients tests/
pylint rabbit_clients/ tests/ > lintscore

if [ -z "$NO_DOCKER" ]
then
  docker stop rabbitmq >> tests.log
  docker rm rabbitmq >> tests.log
fi

deactivate

rm -rf rabbittest

echo "Testing Complete"
