!['build status'](https://travis-ci.org/awburgess/rabbit-clients.svg?branch=master)
![Coverage Status](https://coveralls.io/repos/github/awburgess/rabbit-clients/badge.svg?branch=feature/expand_rabbitmq_config_env)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/awburgess/rabbit-clients)


# Rabbit MQ Clients

Simplify RabbitMQ messaging like a Flask URL Route and enforce
the message body to be JSON


### Installation

From pip

```shell script
$ pip install rabbit-clients
```

From source

```shell script
$ python setup.py install
```

*NOTE:* ```Rabbit-Clients``` looks for the following environment variables:

* ```RABBITMQ_HOST``` - RabbitMQ FQDN, defaults to ```localhost```
* ```RABBITMQ_USER``` - User for authentication, defaults to ```guest```
* ```RABBITMQ_PASSWORD``` - Password for authentication, defaults to ```guest```
* ```RABBITMQ_VIRTUAL_HOST``` - Virtual host, defaults to ```/```
* ```RABBITMQ_PORT``` - Port to use, defaults to ```5672```

### Usage Example

You may only have one ```ConsumeMessage``` decorator per module/service.  A user can publish as much as desired.

```python
from typing import Dict, Any, Union

from rabbit_clients import PublishMessage, ConsumeMessage


@PublishMessage(queue='younguns', exchange='millennials')
def publish_to_younguns(message: Dict[str, Any]) -> Dict[str, Any]:
    return message


@PublishMessage(queue='aaron_detect', exchange='genx')
def check_for_aaron(consumed_message: Dict[str, Any]) -> Dict[str, Any]:
    return_message = {'name': consumed_message['name'], 'isAaron': False}
    if return_message['name']  == 'Aaron':
        return_message['isAaron'] = True
    return return_message


@ConsumeMessage(queue='oldfolks', exchange='genx')
def remove_forty_and_up(message_dict: Union[Dict[str, Any], None] = None):
    """
    Silly example
    
    :param message_dict: Assumes you are using JSON as your message body
    """ 
    people = message_dict['people']
    not_protected_class = [younger for younger in people if younger['age'] < 40]
    message_dict['people'] = not_protected_class
    
    check_for_aaron(message_dict)
    publish_to_younguns(message_dict)


if __name__ == '__main__':
    remove_forty_and_up()  # Listening for messages

```

### Documentation

README.md

### Testing

Running the unit tests requires that a local RabbitMQ instance is available.  The CI/CD implicitly handles this but users are advised to utilize docker:

```shell script
$ docker run -d --hostname test-rabbit --name some-rabbit -p 8080:15672 rabbitmq:3
```

Refer to [RabbitMQ's Official Dockerhub](https://hub.docker.com/_/rabbitmq) for up-to-date details.

Install the package and development requirements

```shell script
$ pip install -r requirements.txt
$ pip install -r requirements-dev.txt
```

Run the tests

```shell script
$ pytest --cov=rabbit_clients
```

### Contributing

```Rabbit-Clients``` will follow a GitFlow guideline.  Users wishing to contribute
should fork the repo to your account.  Feature branches should be created
from the current development branch and open pull requests against the original repo.
