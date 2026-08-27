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
