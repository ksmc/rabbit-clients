from rabbit_clients.clients.base import _create_global_connection, _CONNECTION
from rabbit_clients.clients.base import send_message

if not _CONNECTION:
    _create_global_connection()
