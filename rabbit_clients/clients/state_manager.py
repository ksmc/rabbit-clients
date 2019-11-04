"""
Connection and channel management classes

"""
import os
from typing import Tuple

import pika


class PikachuStateManager:
    """
    PikachuStateManager's sole purpose is to track RabbitMQ connection
    and channel state to determine if a new connection or channel
    is needed upon decorator call in rabbit clients.  TL;DR it's
    an over-glorified tracking system so that I don't have
    global variables all over the place.

    :param username: RabbitMQ user that can publish and consume from connection credentials provided as **kwargs
    :param pw: RabbitMQ user that can publish and consume from connection credentials proavided as **kwargs
    :param `**kwargs`: All keywords are identical to those in pika.ConnectionParamters object.  See https://pika.readthedocs.io/en/stable/modules/parameters.html

    """

    def __init__(self, username: str = 'ENV', pw: str = 'ENV', **kwargs):
        _username = username if not 'ENV' else os.getenv('RABBIT_USER', 'guest')
        _pw = pw if not 'ENV' else os.getenv('RABBIT_PW', 'guest')
        kwargs['credentials'] = pika.PlainCredentials(_username, _pw)
        kwargs['host'] = os.getenv('RABBIT_URL', 'localhost')
        kwargs['heartbeat'] = 0
        self._connect_params = pika.ConnectionParameters(**kwargs)
        self._connection, self._channel = self.create_connection_and_channel()

    def connection_and_channel_are_stable(self) -> Tuple[bool, bool]:
        """
        indicate whether the class should handle a new connection and/or channel

        :return: A tuple with element zero indicating whether the connection is open and element two being the channel
        :rtype: bool
        """
        return self._connection.is_open, self._channel.is_open

    def create_connection_and_channel(self) -> Tuple[pika.BlockingConnection,
                                                     pika.BlockingConnection.channel]:
        """
        Create a connection and channel for use

        :return: Connection and Channel Pika objects

        """
        connection = pika.BlockingConnection(self._connect_params)
        channel = connection.channel()
        return connection, channel

    def ensure_connection_and_channel(self) -> Tuple[pika.BlockingConnection,
                                                     pika.BlockingConnection.channel]:
        """
        Check if the connection and/or channel are down.  Return current if not else return a new connection
        and channel

        :return: Connection and Channel pika objects

        """
        if not any(self.connection_and_channel_are_stable()):
            return self.create_connection_and_channel()
        return self._connection, self._connection.channel()
