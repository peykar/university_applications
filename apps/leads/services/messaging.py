from apps.messaging.services import get_or_create_conversation
from apps.messaging.services import send_system_message as _send_system


def ensure_conversation(lead):
    return get_or_create_conversation(subject=lead)


def send_system_message(
    lead,
    body: str = "",
    *,
    event_type: str = "",
    event_data: dict[str, object] | None = None,
    performed_by=None,
):
    return _send_system(
        lead,
        body,
        event_type=event_type,
        event_data=event_data,
        performed_by=performed_by,
    )
