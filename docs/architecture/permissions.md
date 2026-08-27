# Permission and scope architecture

Authorization requirements are part of product behavior and must be specified
for every capability.

## Customer workspace

A customer may access only domain records belonging to/managed by their User
according to the owning relationship. Applicant-scoped pages must not expose
another customer's Lead by guessing UUIDs.

## Agent workspace

Agent workspace access is organization-scoped.

1. Resolve the active Agent.
2. Revalidate that the current User is an active/authorized member.
3. Query the requested object through an active-Agent-scoped queryset.
4. Return privacy-safe not-found/denied behavior rather than leaking that a
   record exists in another Agent.

A multi-Agent user does not receive an aggregate cross-organization workspace.

## Responsibility

Lead `assigned_to` is operational responsibility. It does not hide the Lead from
other authorized users of the same Agent.

Actions may impose stronger rules. Example: finalization requires the current
Agent user to be the responsible Agent user.

## Organization switching

A requested Agent switch must target an Agent available to the current User.
After switching, only organization-neutral workspace routes may be preserved.
Entity detail URLs are not carried across organizations.

## Messaging

Conversation access requires both:

- correct customer/Agent participant relationship; and
- access to the conversation subject in the current role/scope.

Read state is role-specific even when one User can appear in more than one role.

## Test expectation

For every new protected behavior include:

- authorized positive case;
- wrong customer case where relevant;
- wrong Agent/active-Agent case;
- responsibility-only restriction where relevant;
- malformed/tampered identifier case when the boundary accepts identifiers.
