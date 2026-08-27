# Navigation and workspace architecture

TurkDemy uses a **workspace-first** information architecture. The global site
header is intentionally kept separate from operational navigation.

## 1. Global header

The global header is for discovery and for entering a workspace/account.

### Public discovery

- Universities
- Programs
- FAQ
- About

Contact remains available from the footer and mobile Explore section. It is not
kept in the desktop primary navigation because it is a secondary destination.

### Authenticated controls

Authenticated users see:

- **My TurkDemy** workspace menu
- Language selector
- Account menu

The header must not expose every private feature as a separate top-level link.
In particular, do not add Dashboard, Applicants, Messages, Agent Messages, and
Agent workspace side by side.

## 2. My TurkDemy workspace

`My TurkDemy` is the customer-facing/private workspace.

Its navigation is:

1. **Overview** (`dashboard`)
2. **Applicants**
3. **Messages** with unread badge

The same navigation appears in the global My TurkDemy dropdown and as a
persistent **left sidebar on desktop** throughout customer/private pages. On
small screens the sidebar collapses into a compact horizontal workspace bar.

The URL may continue to be `/dashboard/`; the UI label is **Overview** because
it describes the page's purpose more clearly.

### Applications

Formal applications currently belong to applicants/students and are summarized
on Overview. There is not yet a standalone customer Applications route, so the
workspace navigation intentionally does not contain a dead or misleading
Applications item. Add it only when a dedicated customer application index
exists.

## 3. Applicant context

An Applicant is a business context inside My TurkDemy, not a global workspace.

Applicant pages contain applicant-specific profile data, preferences, programs,
documents, applications and messages. The global customer navigation remains
visible so the user can return to Overview, Applicants or the general Messages
inbox.

Do not create duplicate global links named "Messages" for applicant and agent
messages. Context determines which messages are being displayed.

## 4. Agent workspace

Users who belong to an Agent organization (or superusers) can switch to the
Agent workspace.

The Agent workspace uses a persistent **left sidebar on desktop**. Its navigation order is:

1. Overview
2. Applicants
3. Applications
4. Messages

Both Agent membership roles (`manager` and `agent`) use the same workspace.
Role-based permissions decide which management features are available; there
is no separate Manager workspace.

Agent workspace access is exposed as a **workspace switch**, not as another
ordinary public/header navigation item.

## 5. Account menu

The account menu contains identity/account concerns:

- Profile
- Sign-in methods
- Workspace switcher (when the user has Agent access)
- Logout

Language selection remains separate from the account menu.

## 6. Mobile navigation

Mobile navigation uses explicit groups:

- Explore
- My TurkDemy
- Workspaces (when applicable)
- Account

This mirrors the desktop information architecture rather than flattening all
links into one list.

## 7. Rules for future navigation changes

When adding a new feature, first decide its scope:

- **Discovery/public** → global Explore navigation if important enough.
- **Customer-wide operation** → My TurkDemy navigation.
- **Applicant-specific operation** → applicant context, not global header.
- **Agent-wide operation** → Agent workspace.
- **Identity/security** → Account menu.

Avoid duplicate labels at the same navigation level. Unread badges belong to
the corresponding Messages entry. A workspace switch must always be visually
distinct from navigation within the current workspace.


## 8. Desktop sidebar behavior

Workspace navigation is intentionally rendered as a real sidebar on desktop.

### My TurkDemy

The customer sidebar appears on Overview, Applicants, applicant detail/edit/
preferences pages, and the customer messaging inbox/conversation pages.

### Agent workspace

The Agent sidebar appears on every Agent workspace page and replaces the older
top-tab navigation.

At viewport widths up to 760px the sidebar becomes a horizontal, scrollable
workspace navigation bar so content width remains usable on phones.

The global header remains independent from these sidebars. It provides public
discovery, a My TurkDemy entry point, language, account actions, and workspace
switching; it does not duplicate all sidebar entries.


## 9. Entity-level navigation

TurkDemy has a third navigation level for complex workflow entities. Workspace
navigation answers **which area of TurkDemy am I in?** Entity navigation answers
**which part of this specific record am I viewing?**

### Applicant

Both customer and Agent applicant pages use:

1. Overview
2. Profile
3. Programs
4. Documents
5. Applications
6. Messages

The Applicant navigation is shown below the applicant identity/header and
inside the current workspace content area. The left workspace sidebar remains
visible.

Scope is important:

- Workspace **Messages** = conversations across the workspace.
- Applicant **Messages** = conversation about this applicant.
- Agent workspace **Applications** = all applications managed by the Agent.
- Applicant **Applications** = applications belonging to this applicant.

The existing combined applicant detail remains the **Overview** page. Focused
pages provide dedicated views of profile, programs, documents, applications and
messages.

### Application

Both customer and Agent application pages use:

1. Overview
2. Requirements
3. Documents
4. Activity
5. Messages

An application page is the same resource regardless of whether the user reached
it through the workspace Applications list or through an Applicant's
Applications tab.

Current structured requirements are represented by ApplicationDocument records
marked `is_required`. The Requirements page explicitly reports when no
structured requirements exist.

Application Activity is currently a read-only composed timeline from the
application creation/update timestamps, application documents and
application-scoped messages. If application workflow events become richer,
introduce a dedicated ApplicationActivity model rather than expanding UI-only
inference indefinitely.

### Navigation-level rule

Use entity-level navigation only for entities that represent an ongoing workflow
with multiple independently useful areas. Do not add permanent tabs merely
because a Django model has many fields.

Current decisions:

- Applicant: yes.
- Application: yes.
- Student: no separate navigation identity; it is the validated continuation
  of the applicant/person case.
- University: no entity tabs yet.
- Program: no entity tabs yet.
- Agent organization: may gain entity navigation later for manager-only
  organization management.


See also: [Agent workspace context](agent-workspace-context.md).
