from typing import Dict, NoReturn, Any
import time
import os

import pytest

from rabbit_clients import send_message, receive_message


_DOCKER_UP = os.environ['DOCKER_STATUS']


def test_that_a_message_is_sent_and_received() -> NoReturn:
    """
    Test that a user can send a message using the decorator and then receive said message with the
    send decorator

    :return: None
    """
    @send_message(queue='test', exchange='')
    def issue_message() -> Dict[str, str]:
        return {'lastName': 'Suave', 'firstName': 'Rico', 'call': 'oi-yaaay, oi-yay'}

    @receive_message(queue='test', exchange='')
    def get_message(message_content: Dict[str, Any]):
        assert message_content['lastName'] == 'Suave'
        assert message_content['firstName'] == 'Rico'
        assert message_content['call'] == 'oi-yaaay, oi-yay'

    issue_message()
    time.sleep(2)
    get_message()
