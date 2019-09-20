# Rabbit MQ Clients

A set of client of objects to use in any service that needs to send or receive RabbitMQ messages.

### Installation

```python
python setup.py install
```

### Features

```Rabbit-Clients``` is an opinionated set of decorators for services or solutions
that need to exist as part of a queue oriented ecosystem.  They are opinionated in
that you can only ever have one consumer per service.  This ties services
to queues intentionally as to ensure the services purpose remains
narrow and focused.  Services can publish as much as desired.  See the
examples below for usage

### Usage Example

The easiest example is when you stand up a service that needs to consume
from one queue and then pass on to another.  You need to wrap a function that 
consumes a dictionary and returns a dictionary.  The input parameter
will be fed from the ```consume_queue``` and the output message will be
converted to JSON and send to the "publish_queue".  At present, this function
only supports one consume and one publish queue.

```python
from typing import TypeVar
from rabbit_clients import message_pipeline

RabbitMQMessage = TypeVar('RabbitMQMessage')

@message_pipeline(consume_queue='oldfolks', publish_queue='younguns')
def remove_forty_and_over(message_dict=None) -> RabbitMQMessage:
    # Please note, the author is/was turning 40 around the time this was first written.
    # So don't remove it in a future pull request.  I was here.
    people = message_dict['people']
    not_protected_class = [younger for younger in people if younger['age'] < 40]
    message_dict['people'] = not_protected_class
    return message_dict


if __name__ == '__main__':
    remove_forty_and_over()  # Listening for messages

```

Users can also utilize functions for consuming and publishing independently.  Users must
remember, though, that only one consumer is allowed at a time.

```python
from typing import TypeVar
from rabbit_clients import consume_message, publish_message

RabbitMQMessage = TypeVar('RabbitMQMessage')


@publish_message(queue='younguns')
def publish_to_younguns(message):
    return message


@publish_message(queue='aaron_detect')
def check_for_aaron(consumed_message):
    return_message = {'name': consumed_message['name'], 'isAaron': False}
    if return_message['name']  == 'Aaron':
        return_message['isAaron'] = True
    return return_message


@consume_message(consume_queue='oldfolks')
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