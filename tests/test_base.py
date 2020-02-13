"""
Unit tests for expected purposes of blocking.py

"""

# pylint: disable=unused-variable

from typing import Dict, NoReturn, Any

import pytest

from rabbit_clients import ConsumeMessage, PublishMessage


@pytest.mark.xfail(condition=True, reason='The consumer will block exiting unless we force a timeout')
@pytest.mark.timeout(10)
def test_that_a_message_is_sent_and_received(preprocess_decorators_ret_funcs) -> NoReturn:
    """
    Test that a user can send a message using the decorator and then receive said message with the
    send decorator

    :return: None
    """
    issue_message, get_message, check_log = preprocess_decorators_ret_funcs

    issue_message()

    get_message()


@pytest.mark.xfail(condition=True, reason='The consumer will block exiting unless we force a timeout')
@pytest.mark.timeout(10)
def test_that_received_messages_are_published_to_logging_queue(preprocess_decorators_ret_funcs) -> NoReturn:
    """
    Test that the message and it's metadata are passed to the logging queue upon receive message

    :return: None

    """
    issue_message, get_message, check_log = preprocess_decorators_ret_funcs

    issue_message()

    check_log()

