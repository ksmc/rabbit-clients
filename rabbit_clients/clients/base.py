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
    if not _CONNECTION.is_open:
        _create_global_connection()


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

        if not _CONNECTION.is_open:  # pragma: no cover
            _check_connection()

        _CHANNEL.queue_declare(queue=queue)

        _CHANNEL.basic_publish(
            exchange=exchange,
            routing_key=queue,
            body=json.dumps(result)
        )

    return prepare_channel


def receive_message(queue: str, production_ready: bool=True) -> Any:
    """
    Receive messages from RabbitMQ Server

    :param function: User function to be decorated
    :param:
    :return: Wrapped User Function
    :rtype: Function

    """
    def prepare_channel(func) -> Any:

        if not _CONNECTION.is_open:  # pragma: no cover
            _create_global_connection()

        _CHANNEL.queue_declare(queue=queue)

        def message_handler(ch, method, properties, body):
            return func(json.loads(body))

        if production_ready:  # pragma: no cover

            _CHANNEL.basic_consume(queue=queue, on_message_callback=message_handler, auto_ack=True)

            try:
                _CHANNEL.start_consuming()
            except KeyboardInterrupt:
                _CHANNEL.stop_consuming()
        else:
            method, properties, body = _CHANNEL.basic_get(queue, auto_ack=True)
            if body:
                message_handler(None, None, None, body)

    return prepare_channel
