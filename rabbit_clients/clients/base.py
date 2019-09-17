"""
Base classes for Rabbit

"""
from typing import Any, NoReturn
import os
import json

import pika

_CONNECTION = None
_CHANNEL = None
_HOST = os.environ['RABBIT_URL']


def _create_global_connection() -> NoReturn:
    """
    Will run immediately on library import.  Requires that an environment variable
    for RABBIT_URL has been set.

    """
    global _CONNECTION, _CHANNEL

    _CONNECTION = pika.BlockingConnection(pika.ConnectionParameters(_HOST))
    _CHANNEL = _CONNECTION.channel()


def send_message(queue: str, exchange: str) -> Any:
    """
    Send a message to the RabbitMQ Server

    :param queue: RabbitMQ Queue
    :param exchange: RabbitMQ Exchange
    :return: Wrapped User Function
    :rtype: Function

    """
    def prepare_channel(func, *args, **kwargs) -> Any:

        result = func(*args, **kwargs)

        _CHANNEL.declare_queue(queue=queue)

        _CHANNEL.basic_publish(
            exchange=exchange,
            routing_key=queue,
            body=json.dumps(result)
        )

    return prepare_channel


def receive_message(queue: str, exchange: str) -> Any:
    """
    Receive messages from RabbitMQ Server

    :param function: User function to be decorated
    :return: Wrapped User Function
    :rtype: Function

    """
    def prepare_channel(func) -> Any:

        _CHANNEL.queue_declare(queue=queue)

        def message_handler(ch, method, properties, body):
            return func(body)

        _CHANNEL.basic_consume(queue=queue, on_message_callback=message_handler, auto_ack=True)

        _CHANNEL.start_consuming()

    return prepare_channel
