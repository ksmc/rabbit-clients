from datetime import datetime

from rabbit_clients import ConsumeMessage, PublishMessage


@PublishMessage(queue='test')
def message():
    return {
        'date': str(datetime.now().date()),
        'origin': 'ACL',
        'service_args': {
            'file1': '/something',
            'file2': '/something_as_well',
            'param': 'Ted'
        }
    }


if __name__ == '__main__':
    message()
