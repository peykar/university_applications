from .services import agent_unread_count, customer_unread_count


def message_badges(request):
    if not request.user.is_authenticated:
        return {"agent_unread_message_count": 0, "customer_unread_message_count": 0}
    return {
        "agent_unread_message_count": agent_unread_count(request.user),
        "customer_unread_message_count": customer_unread_count(request.user),
    }
