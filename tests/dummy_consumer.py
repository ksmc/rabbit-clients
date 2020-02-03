import json
from typing import Dict, Any, Union

from rabbit_clients import ConsumeMessage

@ConsumeMessage(queue='test')
def consume(body: Union[Dict[str, Any], None] = None):
    print(json.dumps(body))


if __name__ == '__main__':
    consume()
