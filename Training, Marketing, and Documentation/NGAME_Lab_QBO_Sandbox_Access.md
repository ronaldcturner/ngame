# NGAME College Lab — QuickBooks Sandbox Access

*Standalone guide for early deployments: instructor setup, student sign-in (Intuit ID), and NGAME “mirror” testing.*

**Audience:** Course instructor / NGAME technical contact (primary); students (§ Student sign-in only).

**Related:** Technical install — [INSTALL.md](../INSTALL.md) · FRP daily ops — [FRP_OPERATIONS_GUIDE.md](../FRP_OPERATIONS_GUIDE.md) · Churn example — [NGAME_Churn_Walkthrough.md](NGAME_Churn_Walkthrough.md)

---

## Goal of this lab model

Students act as **bookkeepers**: they post transactions in **one shared QuickBooks Online sandbox company** in the browser. They do **not** install or run NGAME.

You run NGAME on **one surveillance computer** (read-only API). When students edit the **same** sandbox company NGAME watches, you can test as a proxy FRP or “mirror” of their activity on the next training/fraud run.

This is the **cheapest** early path: developer sandbox companies are free; the lab does **not** need paid QBO subscriptions for round one.

---

## Three Intuit identities (do not mix them up)

| What | Who needs it | Cost | What it unlocks |
|------|----------------|------|------------------|
| **Intuit Developer account** | Instructor / NGAME technical contact | Free | [developer.intuit.com](https://developer.intuit.com) — app keys, sandbox company list, “open in QBO” |
| **Paid QBO subscription** | Real operating nonprofits / businesses | Paid | Production companies at [qbo.intuit.com](https://qbo.intuit.com) |
| **Intuit user account (Intuit ID)** | Students (and any invited bookkeeper) | **Free** | Sign in to accept a QBO invite and use the books UI |

**Students need only the third row** — a normal **Intuit ID**. They do **not** enroll as developers, and the college does **not** need lab-wide QBO licenses for this POC.

The sandbox company’s access is already tied to **your** developer sandbox. Students are **guests** on that company, similar to a nonprofit bookkeeper who does not own the QBO subscription.

---

## Two doors into QuickBooks (students use only one)

| Login / URL | Purpose | Students need it? |
|-------------|---------|-------------------|
| **[developer.intuit.com](https://developer.intuit.com)** | App credentials, sandbox list, developer tools | **No** for ledger work |
| **QBO sandbox company** — [sandbox QBO](https://sandbox.qbo.intuit.com) or open company from dev portal once | Invoices, bills, vendors, Audit Log | **Yes** |

**Do not hand students your developer portal username/password.** That exposes app keys and all sandbox companies, not just one lab company. Use **Manage users** invites or a dedicated sandbox company login instead (see § Fallbacks).

---

## How the lab fits NGAME architecture

NGAME is designed for **one surveillance computer**. Bookkeeper machines need only a browser.

```
Student PCs                         Surveillance computer (instructor / lab)
  └─ browser → QBO sandbox company      └─ NGAME → Intuit API (read-only) → same company data
         │                                        └─ dashboard (localhost)
         └──────────── writes ──────────┐
                                        ▼
                              Same sandbox company (cloud)
```

| Role | Location | Tasks |
|------|----------|--------|
| **Student (bookkeeper)** | Any lab PC with browser | Enter/edit QBO transactions; optional Audit Log review per syllabus |
| **Instructor (technical contact)** | One PC with NGAME installed | OAuth once, `quickbooks_config.json`, daily dashboard runs, watch churn |
| **FRP (you, mirroring)** | Same surveillance PC | Run training/fraud checks; review warnings — see FRP guide |

From [INSTALL.md](../INSTALL.md): NGAME **never changes** QuickBooks in the default deployment; it **reads** the same cloud data the bookkeeper edits.

---

## Instructor checklist (before the first class)

1. **Pick one sandbox company** — the same `realm_id` already in your `quickbooks_config.json` (`"environment": "sandbox"`), or create a dedicated “NGAME Lab” sandbox from the developer portal.
2. **Complete NGAME OAuth once** on the surveillance PC as **Master Administrator** or **Company Administrator** (students do not run OAuth).
3. **Test Manage users** (10 minutes): invite your own alternate email; confirm that user can post a test invoice; confirm NGAME still reads that company on the next run.
4. **Bookmark** sandbox QBO for students after you open the company once from the dev portal.
5. **Print or distribute** the student section below (or the HTML version of this handout).
6. **Do not** share developer portal credentials with the class.

---

## Student sign-in — obtaining an Intuit ID (first time)

Students are **not** missing a special “QBO license.” They create or reuse a **free Intuit user account** when they accept **your** invitation to the sandbox company.

### What you do (instructor)

1. Open the lab sandbox company in QBO (sandbox URL or dev portal → open company).
2. Go to **Settings → Manage users → Add user**.
3. Enter the student’s **school email** and a role such as **Standard** (sufficient for invoices, bills, vendors in most labs).
4. Select **Send invitation**.

### What the student does

1. Open the invitation email (“You’re invited to QuickBooks Online”).
2. Click the invite link (invites often **expire in about 48 hours** — ask the instructor to resend if needed).
3. **New to Intuit:** choose **Create an account** and register at [accounts.intuit.com](https://accounts.intuit.com) (email, password, verification). That account **is** their credential.
4. **Already has Intuit:** sign in with an existing Intuit ID (TurboTax, Mint, prior QBO trial, etc.).
5. Accept access to the lab company and complete any role confirmation prompts.

### Ongoing sign-in (every class)

1. Go to [sandbox.qbo.intuit.com](https://sandbox.qbo.intuit.com) (or the bookmark the instructor provides).
2. Sign in with **their** Intuit ID.
3. Select the **lab sandbox company** if prompted.

They should **not** need [developer.intuit.com](https://developer.intuit.com) for normal bookkeeping.

---

## What students do not need

| Item | Needed? |
|------|---------|
| Intuit Developer enrollment | No |
| Paid QBO subscription for the college lab | No (for this sandbox POC) |
| NGAME install, Python, or Terminal | No |
| NGAME OAuth / API authorization | No (instructor only, on surveillance PC) |
| Your developer portal password | **No — do not share** |

---

## NGAME and OAuth (instructor only)

- **OAuth** connects NGAME to a company **once** on the surveillance machine. Only **Master Administrator** or **Company Administrator** can authorize an app connection.
- **Lower roles** (e.g. Standard) may still **enter transactions** in the QBO UI but cannot complete app OAuth. That is expected; students stay in the UI only.
- Tokens and `realm_id` live in `quickbooks_config.json` on the surveillance PC only ([INSTALL.md](../INSTALL.md) § Credentials).

---

## Mirror testing (instructor watches the same ledger)

| Setup | Result |
|-------|--------|
| NGAME `realm_id` = lab sandbox company | Overnight pulls reflect student edits |
| You run **Run Training Day** / fraud check on surveillance PC | Dashboard shows CPI, wCPI, property mutations for that company |
| Students edit invoice amounts, add vendors, etc. | See [NGAME_Churn_Walkthrough.md](NGAME_Churn_Walkthrough.md) for how edits map to signals |

You observe; students change the books. Review the QuickBooks **Audit Log** in the browser per [FRP_OPERATIONS_GUIDE.md](../FRP_OPERATIONS_GUIDE.md) when teaching FRP workflow.

---

## Sandbox caveat — verify before the semester

Intuit documentation stresses that **only admins** can authorize apps. Some developers also report **Manage users** quirks in sandbox (invites failing or limited seats).

**Before relying on per-student invites:**

1. Send one test invite to a non-class email you control.
2. Confirm invitee can sign in and post a test transaction.
3. Run one NGAME training pull and confirm data updates.

If invites fail in your sandbox, use a fallback (next section) for round one — still **without** paid lab licenses.

---

## Access options compared

| Approach | Student credential | Attribution in Audit Log | Share developer portal? |
|----------|-------------------|--------------------------|-------------------------|
| **A. Invite each student** (recommended) | Personal free Intuit ID | Yes | **Never** |
| **B. One shared sandbox company user** | One login you create for the lab | No | **Never** |
| **C. Your developer portal login** | Your password | No | **Avoid** — exposes apps and all sandboxes |

For a **small pilot** (few students, one session), **B** is acceptable. **C** is the wrong credential even if it is the fastest to type.

---

## Optional: Intuit for Education (different use case)

[Intuit for Education](https://www.intuit.com/solutions/education/resources/quickbooks/) offers **free QBO Plus student trials** (school verification via SheerID). That path is valuable for broad accounting coursework where each student needs **their own** company.

It does **not** automatically align with **one shared sandbox company** that your NGAME instance already watches. For “mirror my NGAME” POC testing, stay on **one developer sandbox company + Intuit ID invites** (or shared sandbox login).

---

## Synthetic testing without students

For dry runs without live bookkeepers, the repo includes **anomaly injection** ([ANOMALY_INJECTION_AGENT_README.md](../ANOMALY_INJECTION_AGENT_README.md)). Use it to validate detection; use the lab model above to teach real QBO churn.

---

## Quick reference — who signs in where

| Person | Sign-in | URL |
|--------|---------|-----|
| Instructor (API / NGAME setup) | Developer account + sandbox **admin** for OAuth | [developer.intuit.com](https://developer.intuit.com), then sandbox company |
| Student (bookkeeper) | **Intuit ID** (invited user) | [sandbox.qbo.intuit.com](https://sandbox.qbo.intuit.com) |
| Instructor (FRP-style review) | Sandbox **admin** in browser for Audit Log | Same sandbox company |

---

## File locations (this project)

| Artifact | Path |
|----------|------|
| This handout (Markdown) | `Training, Marketing, and Documentation/NGAME_Lab_QBO_Sandbox_Access.md` |
| Printable (HTML) | `Training, Marketing, and Documentation/NGAME_Lab_QBO_Sandbox_Access.html` |
| NGAME install (technical contact) | `INSTALL.md` |
| FRP operations (dashboard + Audit Log) | `FRP_OPERATIONS_GUIDE.md` / `.html` |

---

*NGAME · College lab QBO sandbox access · May 2026*
