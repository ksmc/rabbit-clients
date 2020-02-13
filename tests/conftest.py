"""
Fixtures for testing
"""
from typing import Dict, Any

import pytest

from rabbit_clients import PublishMessage, ConsumeMessage


@pytest.fixture
def preprocess_decorators_ret_funcs():
    @PublishMessage(queue='test', exchange='testgroup')
    def issue_message() -> Dict[str, str]:
        return {'lastName': 'Suave', 'firstName': 'Rico', 'call': 'oi-yaaay, oi-yay'}

    @ConsumeMessage(queue='test', exchange='testgroup')
    def get_message(message_content: Dict[str, Any]):
        assert message_content['lastName'] == 'Suave'
        assert message_content['firstName'] == 'Rico'
        assert message_content['call'] == 'oi-yaaay, oi-yay'

    @ConsumeMessage(queue='logging')
    def check_log(message_content: Dict[str, Any]):
        assert 'method' in message_content.keys()
        assert 'body' in message_content.keys()
        assert isinstance(message_content['body'], dict)

    return issue_message, get_message, check_log
