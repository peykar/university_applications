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

`My TurkDemy` is the customer-facing/private workspace. Customers see their
end-to-end cases as **Requests**; internal Lead, Student and Application
terminology is not used as customer navigation.

Its sidebar navigation is intentionally menu-only:

1. **My Requests**
2. **Messages** with unread badge
3. **Get Help** → existing Contact page
4. **Message us on WhatsApp** when `WHATSAPP_NUMBER` is configured

The customer sidebar does not render a “MY TURKDEMY” heading, “Student
workspace” subtitle, section labels, or an Agent workspace switch. Workspace
switching remains a global/account concern.

**My Requests** is the authenticated customer landing page. The legacy
`dashboard` route redirects there.

## 3. Request context

A Request is the customer-facing abstraction for the ongoing service case. It
is currently rooted in a Lead internally and may later involve a Student and
formal Applications, but those lifecycle terms remain Agent/internal concepts.

Request pages can expose profile, programs, documents and messages without
requiring the customer to understand backend state transitions. The My Requests
index summarizes the person's name/contact details, all associated program
interests, and attention signals for unread messages or documents that need
replacement.

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
- **Customer-wide operation** → My TurkDemy navigation using customer Request terminology.
- **Request-specific customer operation** → Request context; Agent-side Applicant operations remain internal.
- **Agent-wide operation** → Agent workspace.
- **Identity/security** → Account menu.

Avoid duplicate labels at the same navigation level. Unread badges belong to
the corresponding Messages entry. A workspace switch must always be visually
distinct from navigation within the current workspace.


## 8. Desktop sidebar behavior

Workspace navigation is intentionally rendered as a real sidebar on desktop.

### My TurkDemy

The customer sidebar appears on My Requests, request detail/edit/preferences pages, and the customer messaging inbox/conversation pages.

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

### Customer Request / Agent Applicant

Customer pages use Request terminology and expose focused Overview, Profile,
Programs, Documents and Messages areas. The customer navigation does not expose
a separate Applications tab; formal application lifecycle is an internal Agent
concept.

Agent Applicant pages continue to use Applicant terminology and their full
operational navigation, including Applications, Todos and Communication Log.

Scope is important:

- Workspace **Messages** = conversations across the customer workspace.
- Request **Messages** = conversation about this request.
- Agent workspace **Applications** = all applications managed by the Agent.
- Agent Applicant **Applications** = applications belonging to this applicant.

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


See also: [Agent applicant workspace](agent-applicant-workspace.md).

### Request-local navigation

Within a selected customer Request, the central workspace owns the Request tabs:
Overview, Profile, Programs, Documents and Messages. A separate right context
sidebar persists alongside these tabs and shows Uploaded documents and Program
preferences; it does not replace Request-local navigation.

## 7. Shared footer

The footer uses the same customer-facing workspace language as the rest of TurkDemy. The private-workspace group is **My TurkDemy**, not the legacy **Students** group. Authenticated users receive **My Requests** and **Messages** links; signed-out visitors receive **Login**. Legacy **Dashboard / Profile** footer links are intentionally removed because the customer landing page and navigation are Request-based.

### Mobile customer workspace actions

The customer workspace navigation uses an adaptive narrow-screen grid so My Requests, Messages, Get Help, and the optional WhatsApp action remain visible without horizontal clipping. Long support labels may wrap inside their cell; if WhatsApp is not configured, the remaining actions redistribute automatically.


## Customer Request tabs

The canonical customer Request tab navigation is **Overview · Profile · Preferences · Programs · Documents · Messages**. Preferences represents what the customer is looking for; Programs represents concrete programs being considered. On mobile, the six tabs remain on one line in a horizontally scrollable strip rather than being compressed into equal-width columns.
