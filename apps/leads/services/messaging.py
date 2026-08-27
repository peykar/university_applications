from apps.messaging.services import get_or_create_conversation
from apps.messaging.services import send_system_message as _send_system


def ensure_conversation(lead):
    return get_or_create_conversation(subject=lead)


def send_system_message(lead, body: str, *, performed_by=None):
    return _send_system(lead, body, performed_by=performed_by)
