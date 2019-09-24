"""
Base classes for Rabbit

"""
from typing import Any, NoReturn, Dict, Union, List
import os
import json

import pika

_CONNECTION = None
_CHANNEL = None
_HOST = os.environ.get('RABBIT_URL', 'localhost')


def _create_global_connection() -> NoReturn:
    """
    Will run immediately on library import.  Requires that an environment variable
    for RABBIT_URL has been set.

    :return: None
    """
    global _CONNECTION, _CHANNEL

    _CONNECTION = pika.BlockingConnection(pika.ConnectionParameters(_HOST))
    _CHANNEL = _CONNECTION.channel()


def _check_connection() -> NoReturn:  # pragma: no-cover
    """
    Checks to make sure a connection didn't close; reopens everything if true

    :return: None
    """
    if not _CONNECTION:
        _create_global_connection()

    if not _CONNECTION.is_open:
        _create_global_connection()


def publish_message(queue: str, exchange: str = '') -> Any:
    """
    Send a message to the RabbitMQ Server

    :param queue: RabbitMQ Queue
    :param exchange: RabbitMQ Exchange
    :return: Wrapped User Function
    :rtype: Function

    """
    def inner_function(func):
        def prepare_channel(*args, **kwargs) -> NoReturn:
            """
            Run the function as expected but the return from the function must
            be a Python dictionary as it will be converted to JSON. Then ensure
            RabbitMQ connection is open and that you have an open channel.  Then
            use a basic_publish method to send the message to the target queue.

            :param args:  Any positional arguments passed to the function
            :param kwargs: Any keyword arguments pass to the function
            :return: None

            """

            # Run the function and get dictionary as result
            result = func(*args, **kwargs)

            # Ensure open connection and channel
            _check_connection()

            # Ensure queue exists
            _CHANNEL.queue_declare(queue=queue)

            # Send message to queue
            _CHANNEL.basic_publish(
                exchange=exchange,
                routing_key=queue,
                body=json.dumps(result)
            )

        return prepare_channel
    return inner_function


def consume_message(consume_queue: str, publish_queues: Union[str, List[str]] = None, exchange: str = '',
                    production_ready: bool = True) -> Any:
    """
    Receive messages from RabbitMQ Server

    :param consume_queue: The queue from which to receive messages
    :param publish_queues: The queue(s) to send messages to
    :param exchange: The exchange to target if any
    :param production_ready: Keyword argument that will make this
    decorator only return one message from the queue rather than listen
    if set to False; default True
    :return: Wrapped User Function
    :rtype: Function

    """
    def inner_function(func):

        def prepare_channel() -> Any:
            """
            Ensure RabbitMQ Connection is open and that you have an open
            channel.  Then provide a callback returns the target function
            but ensures that the incoming message body has been
            converted from JSON to a Python dictionary.

            :param func: The user function being decorated
            :return: An open listener utilizing the user function or
            a one time message receive in the event of parent function
            parameter of production ready being set to False

            """

            # Open RabbitMQ connection if it has closed or is not set
            _check_connection()

            # Ensure the queue we want to write to has been created
            _CHANNEL.queue_declare(queue=consume_queue)

            # Callback function for when a message is received
            def message_handler(channel, method, properties, body):

                # Utilize module decorator to send logging messages
                @publish_message(queue='logging', exchange='')
                def send_log() -> Dict[str, str]:
                    """
                    Send message details and body as JSON to logging
                    queue

                    :return: All message elements as Python dictionary
                    :rtype: dict

                    """
                    return {
                        'channel': channel,
                        'method': method,
                        'properties': properties,
                        'body': json.loads(body)
                    }

                if publish_queues:
                    publish_message(queue=publish_queues, exchange=exchange)(func)(json.loads(body))

            # Open up listener with callback
            if production_ready:  # pragma: no cover

                _CHANNEL.basic_consume(queue=consume_queue, on_message_callback=message_handler, auto_ack=True)

                try:
                    _CHANNEL.start_consuming()
                except KeyboardInterrupt:
                    _CHANNEL.stop_consuming()

            # Consume one message and stop listening
            else:
                method, properties, body = _CHANNEL.basic_get(consume_queue, auto_ack=True)
                method = str(method)
                properties = str(properties)

                if body:
                    message_handler(None, None, None, body)
                    @publish_message(queue='logging', exchange='')
                    def send_log() -> Dict[str, str]:
                        """
                        Send message details and body as JSON to logging
                        queue

                        :return: All message elements as Python dictionaary
                        :rtype: dict

                        """
                        return {
                            'method': method,
                            'properties': properties,
                            'body': json.loads(body)
                        }

        return prepare_channel
    return inner_function


def message_pipeline(consume_queue: str, publish_queue: str, exchange: str = '', production_ready: bool = True):
    """
    Convenience decorator when you need an to consume from a message queue and publish back to a queue

    :param consume_queue: Queue from which to consume
    :param publish_queues: Queue for publishing
    :param exchange: Exchange if set; default ''
    :param production_ready: If False, consumes one message and stops; default: True
    :return:function
    """
    def inner_function(func):
        def wrapper(message_dict):
            consume_message(consume_queue=consume_queue, publish_queues=publish_queue,
                            exchange=exchange, production_ready=production_ready)(func)(message_dict)
        return wrapper
    return inner_function


