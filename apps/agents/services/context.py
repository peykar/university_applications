from __future__ import annotations

from django.core.exceptions import PermissionDenied

from apps.agents.models import Agent

ACTIVE_AGENT_SESSION_KEY = "active_agent_id"


def available_agents(user):
    if not user.is_authenticated:
        return Agent.objects.none()
    if user.is_superuser:
        return Agent.objects.filter(is_active=True).order_by("company_name")
    return user.agents.filter(is_active=True).order_by("company_name")


def resolve_active_agent(request, *, required: bool = True):
    """Resolve the current Agent and never trust the session without membership validation."""
    agents = available_agents(request.user)
    active_agent_id = request.session.get(ACTIVE_AGENT_SESSION_KEY)

    if active_agent_id:
        try:
            active_agent = agents.filter(pk=active_agent_id).first()
        except (TypeError, ValueError):
            active_agent = None
        if active_agent is not None:
            return active_agent
        request.session.pop(ACTIVE_AGENT_SESSION_KEY, None)

    membership_count = agents.count()
    if membership_count == 1:
        active_agent = agents.first()
        if active_agent is not None:
            request.session[ACTIVE_AGENT_SESSION_KEY] = str(active_agent.pk)
            return active_agent

    if membership_count > 1:
        if required:
            raise PermissionDenied("Choose an Agent organization to enter its workspace.")
        return None

    if required:
        raise PermissionDenied("An active agent membership is required.")
    return None


def switch_active_agent(request, agent_id):
    """Switch only to an Agent that the current user is authorized to access."""
    try:
        agent = available_agents(request.user).filter(pk=agent_id).first()
    except (TypeError, ValueError):
        agent = None
    if agent is None:
        raise PermissionDenied("You are not a member of this Agent.")
    request.session[ACTIVE_AGENT_SESSION_KEY] = str(agent.pk)
    return agent
