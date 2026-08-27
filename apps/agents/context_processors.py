from __future__ import annotations

from apps.messaging.services import agent_unread_count

from .services.context import available_agents, resolve_active_agent


def agent_workspace(request):
    if not request.user.is_authenticated:
        return {
            "active_agent": None,
            "available_agent_workspaces": (),
            "agent_unread_message_count": 0,
        }

    agents = list(available_agents(request.user))
    if not agents:
        return {
            "active_agent": None,
            "available_agent_workspaces": (),
            "agent_unread_message_count": 0,
        }

    active_agent = resolve_active_agent(request, required=False)
    return {
        "active_agent": active_agent,
        "available_agent_workspaces": agents,
        "agent_unread_message_count": (
            agent_unread_count(request.user, agent=active_agent) if active_agent is not None else 0
        ),
    }
