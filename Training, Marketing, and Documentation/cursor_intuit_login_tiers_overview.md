# Intuit login tiers overview
_Exported on 6/3/2026 at 12:55:26 PDT from Cursor (3.6.31)_

---

**User**

how to sign in to Intuit (licensed QBO user, developer, simple ID only (no license, but can use QBO to manipulate the sandbox data used in this project). You listed these three tiers of logins somewhere. Can you extract that table and reproduce it here?

---

**Cursor**

Searching the project and prior context for the Intuit/QBO login tiers table.


Reading the full section from the lab guide for complete context.


The three-tier table is in **`Training, Marketing, and Documentation/NGAME_Lab_QBO_Sandbox_Access.md`** under **“Three Intuit identities (do not mix them up)”**. Here it is, with your labels mapped to the doc’s wording.

## Three Intuit identities

| What | Who needs it | Cost | What it unlocks |
|------|----------------|------|------------------|
| **Intuit Developer account** | Instructor / NGAME technical contact | Free | [developer.intuit.com](https://developer.intuit.com) — app keys, sandbox company list, “open in QBO” |
| **Paid QBO subscription** | Real operating nonprofits / businesses | Paid | Production companies at [qbo.intuit.com](https://qbo.intuit.com) |
| **Intuit user account (Intuit ID)** | Students (and any invited bookkeeper) | **Free** | Sign in to accept a QBO invite and use the books UI |

**Your labels → doc rows**

| Your term | Row |
|-----------|-----|
| **Developer** | Intuit Developer account |
| **Licensed QBO user** | Paid QBO subscription (production) |
| **Simple ID only** (no license) | Intuit ID — invited guest on sandbox/production company |

**For this project’s sandbox lab:** students need **only row 3** (Intuit ID). They do **not** need developer enrollment or a paid QBO license. The college does **not** need lab-wide QBO subscriptions for the POC.

---

## Who signs in where (quick reference)

| Person | Sign-in | URL |
|--------|---------|-----|
| Instructor (API / NGAME setup) | Developer account + sandbox **admin** for OAuth | [developer.intuit.com](https://developer.intuit.com), then sandbox company |
| Student (bookkeeper) | **Intuit ID** (invited user) | [sandbox.qbo.intuit.com](https://sandbox.qbo.intuit.com) |
| Instructor (FRP-style review) | Sandbox **admin** in browser for Audit Log | Same sandbox company |

---

## Two doors (students use only one)

| Login / URL | Purpose | Students need it? |
|-------------|---------|-------------------|
| **[developer.intuit.com](https://developer.intuit.com)** | App credentials, sandbox list, developer tools | **No** for ledger work |
| **QBO sandbox** — [sandbox.qbo.intuit.com](https://sandbox.qbo.intuit.com) | Invoices, bills, vendors, Audit Log | **Yes** |

**Student ongoing sign-in:** [sandbox.qbo.intuit.com](https://sandbox.qbo.intuit.com) → their Intuit ID → select the lab sandbox company. They should **not** use the developer portal for normal bookkeeping.

Full handout (including invite steps): `Training, Marketing, and Documentation/NGAME_Lab_QBO_Sandbox_Access.md` (HTML: `NGAME_Lab_QBO_Sandbox_Access.html`).

---

**User**

I've forgotten. How does a new Intuit ID user prompt Intuit to offer him/her an invitation?

---

**Cursor**

Checking the lab guide for the exact invitation flow — whether the student initiates anything or only responds to an invite.


They **don’t**. Intuit does not offer a QBO company invitation because someone created an Intuit ID or signed in at [accounts.intuit.com](https://accounts.intuit.com). Invitations are **always sent by a company admin** from inside QuickBooks.

## How it actually works

**Instructor / company admin (you):**

1. Open the lab sandbox company in QBO ([sandbox.qbo.intuit.com](https://sandbox.qbo.intuit.com) or via the developer portal).
2. **Settings → Manage users → Add user**
3. Enter the student’s **email** (must match what they’ll use for Intuit ID) and a role (e.g. **Standard**).
4. **Send invitation**

**New student (passive — no “request invite” step):**

1. Wait for email: **“You’re invited to QuickBooks Online”**
2. Click the link in that email (often expires in ~48 hours; admin resends if needed)
3. On the accept flow:
   - **New to Intuit:** **Create an account** → that becomes their Intuit ID
   - **Already has Intuit ID:** sign in with existing credentials
4. Accept access to the lab company

**After that (every class):** go to sandbox QBO → sign in with **their** Intuit ID → pick the lab company if asked.

## What the student should *not* do

- Sign up at the developer portal expecting an invite
- Buy or start a QBO trial hoping to “join” your sandbox
- Ask Intuit support for access to your company

None of those paths connect them to **your** sandbox. Only the **Manage users** invite (or a shared lab login you create) does.

## If they already made an Intuit ID with no invite

Give you the **same email** they used, then you send **Add user** from Manage users. They accept via the new email link — they don’t “prompt” Intuit; they just complete the invite you sent.

**Small pilot fallback:** one shared sandbox user you create for the class (no per-student invites) — see the lab guide’s access options table.

