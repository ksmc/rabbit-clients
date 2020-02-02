"""
Unit tests for expected purposes of blocking.py

"""

# pylint: disable=unused-variable

from typing import Dict, NoReturn, Any
import time

from rabbit_clients import ConsumeMessage, PublishMessage


def test_that_a_message_is_sent_and_received() -> NoReturn:
    """
    Test that a user can send a message using the decorator and then receive said message with the
    send decorator

    :return: None
    """
    @PublishMessage(queue='test', exchange='')
    def issue_message() -> Dict[str, str]:
        return {'lastName': 'Suave', 'firstName': 'Rico', 'call': 'oi-yaaay, oi-yay'}

    # pytest may execute faster than the message is able to be read, pause for 5 seconds
    time.sleep(5)

    @ConsumeMessage(queue='test')
    def get_message(message_content: Dict[str, Any]):
        assert message_content['lastName'] == 'Suave'
        assert message_content['firstName'] == 'Rico'
        assert message_content['call'] == 'oi-yaaay, oi-yay'


def test_that_received_messages_are_published_to_logging_queue() -> NoReturn:
    """
    Test that the message and it's metadata are passed to the logging queue upon receive message

    :return: None

    """
    @PublishMessage(queue='test', exchange='')
    def issue_message() -> Dict[str, str]:
        return {'lastName': 'Suave', 'firstName': 'Rico', 'call': 'oi-yaaay, oi-yay'}

    # pytest may execute faster than the message is able to be read, pause for 5 seconds
    time.sleep(5)

    @ConsumeMessage(queue='logging')
    def check_log(message_content: Dict[str, Any]):
        assert 'method' in message_content.keys()
        assert 'body' in message_content.keys()
        assert isinstance(message_content['body'], dict)

