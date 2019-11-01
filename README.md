# Rabbit MQ Clients

An attempt to simplify RabbitMQ messaging like a Flask URL Route


### Installation

From pip

```bash
$ pip install rabbit-clients
```

From source

```python
python setup.py install
```

*NOTE:* ```Rabbit-Clients``` looks for the following environment variables:

* ```RABBIT_URL``` - RabbitMQ FQDN, defaults to ```localhost```
* ```RABBIT_USER``` - User for authentication, defaults to ```guest```
* ```RABBIT_PW``` - Password for authentication, defaults to ```guest```


### Usage Example

You may only have one consumer per module/service.  A user can publish as much as desired.

```python
from typing import TypeVar
from rabbit_clients import PublishMessage, ConsumeMessage

RabbitMQMessage = TypeVar('RabbitMQMessage')


@PublishMessage(queue='younguns')
def publish_to_younguns(message):
    return message


@PublishMessage(queue='aaron_detect')
def check_for_aaron(consumed_message):
    return_message = {'name': consumed_message['name'], 'isAaron': False}
    if return_message['name']  == 'Aaron':
        return_message['isAaron'] = True
    return return_message


@ConsumeMessage(consume_queue='oldfolks')
def remove_forty_and_up(message_dict):
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

### How to run unit tests

Unit testing is done with ```pytest``` and is
orchestrated by a single shell script that runs a 
RabbitMQ instance in Docker

```bash
./test.sh
```

### Contributing

```Rabbit-Clients``` will follow a GitFlow guideline.  Users wishing to contribute
should fork the repo to your account.  Feature branches should be created
from the current development branch and open pull requests against the original repo.
