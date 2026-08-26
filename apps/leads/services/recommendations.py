"""Automatic program recommendations are intentionally disabled.

TurkDemy keeps applicant programs simple: programs are either added by the
customer or suggested by an agent. Automated/system-suggested program
associations are not part of the workflow.
"""


def recommend_programs_for_lead(*args, **kwargs):
    raise NotImplementedError(
        "Automatic/system program suggestions are disabled. "
        "Programs must be user-added or agent-suggested."
    )
