"""
Base classes for Rabbit

"""
from typing import Any, Dict, Union, List, Tuple
import os
import json

import pika

try:
    from state_manager import PikachuStateManager
except ImportError:
    from rabbit_clients.clients.state_manager import PikachuStateManager


def _create_connection_and_channel() -> Tuple[pika.BlockingConnection, pika.BlockingConnection.channel]:
    """
    Will run immediately on library import.  Requires that an environment variable
    for RABBIT_URL has been set.

    :return: Tuple as rabbitmq connection and channel
    :rtype: tuple

    """
    host = os.getenv('RABBIT_URL', 'localhost')
    user = os.getenv('RABBIT_USER', 'guest')
    pw = os.getenv('RABBIT_PW', 'guest')

    credentials = pika.PlainCredentials(user, pw)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host, credentials=credentials))
    return connection, connection.channel()


def send_log(channel: Any, method: str, properties: Any, body: str) -> Dict[str, Any]:
    """
    Helper function to send messages to logging queue

    :param channel: Channel from incoming message
    :param method: Method from incoming message
    :param properties: Properties from incoming message
    :param body: JSON from incoming message
    :return: Dictionary representation of message

    """
    return {
        'channel': channel,
        'method': method,
        'properties': properties,
        'body': json.loads(body)
    }


class ConsumeMessage:

    def __init__(self, consume_queue: str, publish_queues: Union[str, List[str]] = None, exchange: str = '',
                 production_ready: bool = True, logging: bool = True, logging_queue: str = 'logging'):
        self._consume_queue = consume_queue
        self._publish_queues = publish_queues
        self._exchange = exchange
        self._production_ready = production_ready
        self._logging = logging
        self._logging_queue = logging_queue
        self._manager = PikachuStateManager()

    def __call__(self, func, *args, **kwargs) -> Any:
        def prepare_channel(*args, **kwargs):
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
            connection, channel = self._manager.ensure_connection_and_channel()

            log_publisher = PublishMessage(queue=self._logging_queue)
            queue_publish = PublishMessage(queue=self._publish_queues, exchange=self._exchange)

            # Callback function for when a message is received
            def message_handler(channel, method, properties, body):

                # Utilize module decorator to send logging messages
                if self._logging:
                    log_publisher(send_log)(channel, method, properties, body)

                if self._publish_queues:
                    queue_publish(func)(json.loads(body))
                else:
                    func(json.loads(body))

            # Open up listener with callback
            if self._production_ready:  # pragma: no cover

                channel.basic_consume(queue=self._consume_queue, on_message_callback=message_handler, auto_ack=True)

                try:
                    channel.start_consuming()
                except KeyboardInterrupt:
                    channel.stop_consuming()

            # Consume one message and stop listening
            else:
                method, properties, body = channel.basic_get(self._consume_queue, auto_ack=True)

                if body:
                    message_handler(None, None, None, body)
                    if self._logging:
                        PublishMessage(queue=self._logging_queue)(send_log)(None, None, None, body)

        return prepare_channel


class PublishMessage:
    def __init__(self, queue: str, exchange: str = ''):
        self._queue = queue
        self._exchange = exchange
        self._manager = PikachuStateManager()

    def __call__(self, func, *args, **kwargs) -> Any:
        def wrapper(*args, **kwargs):
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
            connection, channel = self._manager.ensure_connection_and_channel()

            # Ensure queue exists
            channel.queue_declare(queue=self._queue)

            # Send message to queue
            channel.basic_publish(
                exchange=self._exchange,
                routing_key=self._queue,
                body=json.dumps(result)
            )
        return wrapper
