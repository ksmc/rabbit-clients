# Rabbit MQ Clients

A set of client of objects to use in any service that needs to send or receive RabbitMQ messages.
This is system specific for 

### Installation

```python
python setup.py install
```

### Usage Example

The easiest example is when you stand up a service that needs to consume
from one queue and then pass on to another.  You need to wrap a function that 
consumes a dictionary and returns a dictionary.  The input parameter
will be fed from the ```consume_queue``` and the output message will be
converted to JSON and send to the "publish_queue".  At present, this method
only supports one consume and one publish queue.

```python
from typing import TypeVar
from rabbit_clients import message_pipeline

RabbitMQMessage = TypeVar('RabbitMQMessage')

@message_pipeline(consume_queue='oldfolks', publish_queue='younguns')
def remove_forty_and_over(message_json_as_dict=None) -> RabbitMQMessage:
    # Please note, the author is/was turning 40 around the time this was first written.
    # So don't remove it in a future pull request.  I was here.
    people = message_json_as_dict['people']
    not_protected_class = [younger for younger in people if younger['age'] < 40]
    message_json_as_dict['people'] = not_protected_class
    return message_json_as_dict


if __name__ == '__main__':
    remove_forty_and_over()

```

