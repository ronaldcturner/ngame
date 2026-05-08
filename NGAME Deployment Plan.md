# NGAME Deployment Plan
_Exported on 4/30/2026 at 12:29:33 PDT from Cursor (3.2.11)_

---

**User**

Need to leave the Intuit Developer environment and access a customer's actual QBO account via OAuth.  I won't have the Developer's prompts in order to get the necessary OAuth id's, secretts, and the rest. How do I set up that OAuth process?

---

**Cursor**

Let me look at the project context first to understand what integration is already in place.

Good news: your project already has a solid OAuth implementation in `ngame_quickbooks_oauth.py`. Here's what you need to understand about the full picture, because there's a common misconception worth clearing up first.

---

## The Fundamental Model

You **always** need an Intuit Developer account — but it's **yours**, not the customer's. Here's the separation of concerns:

| Who | What they provide |
|---|---|
| **You (the developer)** | `client_id` and `client_secret` — from your registered app in the [Intuit Developer Portal](https://developer.intuit.com) |
| **The customer** | Authorization — they click "Connect to QuickBooks" and grant your app access to their company (`realm_id`) |

The OAuth flow exchanges those two things for tokens your app uses to read the customer's data. There is no path that skips the developer portal; the `client_id`/`client_secret` pair is what proves to Intuit that your application is legitimate.

---

## Step-by-Step Setup for a Real Customer Account

### 1. Create / configure your Intuit app for Production

1. Go to [developer.intuit.com](https://developer.intuit.com) → **My Apps → Create an App → QuickBooks Online and Payments**.
2. Under **Keys & OAuth**, you'll see both **Sandbox** and **Production** keys. Copy the **Production** `Client ID` and `Client Secret`.
3. Under **Redirect URIs**, add exactly the URI your local server will listen on. Your code defaults to `http://localhost:8000/callback` — add that (or whatever port you prefer). Intuit requires this to match exactly.

### 2. Update `quickbooks_config.json`

Change `environment` from `"sandbox"` to `"production"` and paste your production credentials:

```json
{
  "quickbooks_api": {
    "client_id": "YOUR_PRODUCTION_CLIENT_ID",
    "client_secret": "YOUR_PRODUCTION_CLIENT_SECRET",
    "access_token": "",
    "refresh_token": "",
    "realm_id": "",
    "environment": "production",
    "redirect_uri": "http://localhost:8000/callback"
  }
}
```

Or, preferably (to keep secrets out of the file), set environment variables and leave the file token-only:

```bash
export QBO_CLIENT_ID="YOUR_PRODUCTION_CLIENT_ID"
export QBO_CLIENT_SECRET="YOUR_PRODUCTION_CLIENT_SECRET"
export QBO_ENVIRONMENT="production"
```

### 3. Run the interactive OAuth flow once per customer

Your existing `ensure_quickbooks_auth()` function already handles this automatically. When `access_token` and `refresh_token` are blank, it falls through to the interactive path (lines 266–306 in `ngame_quickbooks_oauth.py`):

1. It opens a browser to Intuit's authorization page.
2. The **customer** signs into their QBO account and clicks **Authorize**.
3. Intuit redirects back to `localhost:8000/callback` with a `code` and `realmId`.
4. Your local server captures them, exchanges the code for tokens, and writes everything back to `quickbooks_config.json`.

From that point on, the refresh token handles re-authorization silently until it expires (~100 days of inactivity) or the customer revokes access.

### 4. Trigger that first-time flow

The simplest way is to call `ensure_quickbooks_auth` directly from the command line:

```python
# one-time bootstrap script (save as bootstrap_oauth.py)
from ngame_quickbooks_oauth import ensure_quickbooks_auth, default_quickbooks_config_path

bundle = ensure_quickbooks_auth(default_quickbooks_config_path())
print(f"Authorized. Realm ID: {bundle.realm_id}")
```

Run it with:

```bash
python bootstrap_oauth.py
```

The browser will open, the customer authorizes, and `quickbooks_config.json` will be populated with live production tokens.

---

## Key Differences: Sandbox vs. Production

| Setting | Sandbox | Production |
|---|---|---|
| `environment` | `"sandbox"` | `"production"` |
| `client_id` / `client_secret` | From **Development** keys tab | From **Production** keys tab |
| Customer's data | Intuit test data only | Real customer QBO company |
| Redirect URI | Must be registered in portal | Must be registered in portal |
| `realm_id` | Intuit-generated test company ID | Customer's actual company ID |

---

## What You Do NOT Need

- You do **not** need the customer's Intuit developer credentials.
- You do **not** need anything from inside their QBO account settings.
- You do **not** need to touch the Intuit portal again after initial app setup — the OAuth flow is entirely self-contained once your `client_id`/`client_secret` are in place.

The customer just needs to be the QBO company **owner or admin** (to grant authorization) and have internet access to complete the browser-based consent screen.

---

**User**

Clarify and correct my misconception or over-expectation. For the real go-live, I want NGAME to run on a customer's "Surveillance" computer, not mine. I want for the customer, using their own Surveillance computer, to access their own (the customer's) QBO from the bookkeeper's machine.. The customer should not be an Intuit Developer. All of NGAME must install and run on the Surveillance machine. That machinr belongs to the financiallly responsible persion (FRP). That person runs the training phase, watches his dashboard for warnings, and runs any further enhancements. The FRP is not a developer and should not have to subscribe to Intuit's developer program.  I.E. The NGAME "customer" is the FRP.

---

**Cursor**

This is an important architectural clarification, and your mental model is actually correct for the end goal. The misconception is smaller than you think. Let me lay it out clearly.

---

## The Misconception: Who Registers the App

You are right that the FRP should never touch the Intuit Developer Portal. But **someone** must register NGAME as an application with Intuit — exactly once, ever — and that person is **you (Ron)**, not the customer.

This is identical to how every QBO integration in the world works:

- **Gusto** (payroll) registered their app with Intuit. Their customers never become Intuit developers. Customers just click "Connect to QuickBooks."
- **Bill.com** did the same.
- **NGAME** will do the same.

The `client_id` and `client_secret` are **NGAME's identity as a software product** — not the customer's credentials. You register the app once, you bundle those credentials into the software you distribute, and you never expose them to the FRP.

---

## The Two-Layer Credential Model

| Layer | What it is | Who owns it | Where it lives |
|---|---|---|---|
| **App credentials** | `client_id`, `client_secret` | You (Ron / NGAME LLC) | Bundled into the NGAME installation — FRP never sees these |
| **Customer tokens** | `access_token`, `refresh_token`, `realm_id` | The FRP's QBO company | Written to `quickbooks_config.json` on the Surveillance computer after one-time consent |

---

## The FRP's Actual Experience

1. Install NGAME on the Surveillance computer (one installer, no developer setup).
2. Run NGAME for the first time.
3. A browser opens: **"NGAME wants to access your QuickBooks company. Sign in to authorize."**
4. The FRP logs into their own QBO account (the same one the bookkeeper uses) and clicks **Connect**.
5. Browser says "NGAME: OAuth complete. You can close this tab."
6. Done. NGAME now has a refresh token that lasts ~100 days of inactivity and silently renews on every run.

The FRP never touches the Intuit Developer Portal. They never see a `client_id`. They just log into their own QBO.

---

## What This Requires You to Do (Once)

1. **Register NGAME as a production app** at [developer.intuit.com](https://developer.intuit.com).
2. Get your production `client_id` and `client_secret`.
3. **Bundle those into the NGAME distribution** — not in `quickbooks_config.json` (which is customer-writable), but in a separate read-only location (environment variable injected at install time, a protected config file, or compiled in). The current code already supports `QBO_CLIENT_ID` / `QBO_CLIENT_SECRET` as env vars, which is the right hook for this.
4. Ship it.

**Note on Intuit's review process:** For production access to real QBO companies, Intuit requires an app review before you can serve more than ~25 companies. For a controlled rollout to a handful of FRP customers, you can operate under the "development" tier of a production app while the formal review is pending.

---

## What Needs to Change in the Current Codebase

Right now `quickbooks_config.example.json` puts `client_id` and `client_secret` alongside the customer tokens — implying the FRP fills them in. That needs to be restructured so the FRP's config only contains what belongs to them:

```json
{
  "quickbooks_api": {
    "access_token": "",
    "refresh_token": "",
    "realm_id": "",
    "environment": "production",
    "redirect_uri": "http://localhost:8000/callback"
  }
}
```

And the app credentials arrive via the installer (as `QBO_CLIENT_ID` / `QBO_CLIENT_SECRET` in the shell environment, a `.env` file the installer writes, or an OS keychain entry). Your `ngame_quickbooks_oauth.py` already reads those env vars and already strips them from the JSON it writes back — so the plumbing is already correct. Only the documentation and example config need to reflect this intent.

---

## Summary

| What you thought was needed | Reality |
|---|---|
| FRP needs an Intuit Developer account | No — you register NGAME as an app once |
| FRP fills in `client_id` / `client_secret` | No — those are bundled in the NGAME installer by you |
| FRP does something technical with OAuth | No — they just click "Connect to QuickBooks" in a browser |
| FRP manages tokens | No — NGAME auto-refreshes silently on every run |

Your deployment vision is sound. NGAME is a product; you are its publisher; the FRP is just an end user who consents to QBO access once. That is exactly how every commercial QBO integration works.

---

**User**

Good. That response is a well-compartmentalized deploymehnt roadmap for the end product. Now fell back to my current develement environment. I'm ready to field-test NGAME with a trustied and trusting organization, a small non-profit. They know that this is a testing period only, but they're willing to trust me as a consultant and still as a developer to play the role of the FRP. For this scenario, I assume that there is very little I need to do or that this "test site" non-profit organization needs to do. I'll appreciate the same table-style response that you've provided so far.

---

**Cursor**

## Field Test with the Non-Profit: What's Actually Required

### The short answer: Almost nothing from the non-profit, a few small steps from you.

---

### What the Non-Profit Needs to Do

| Task | Details | Effort |
|---|---|---|
| Have an active QBO subscription | They almost certainly already do | Zero — pre-existing |
| Designate one QBO admin to authorize | The person who clicks "Connect" must have QBO Admin or Company Admin rights | 2 minutes, one time |
| Be present (or hand you their login) for the OAuth consent screen | They log into their own QBO and click Authorize | 2 minutes, one time |

That is the complete list. No installs, no accounts, no technical knowledge required.

---

### What You Need to Do

| Task | How | One-time or recurring |
|---|---|---|
| Switch to your app's **Production keys** in the Intuit Developer Portal | Your existing app already has a Production tab alongside Sandbox — copy the Production `Client ID` and `Client Secret` | One-time |
| Update `quickbooks_config.json` on your machine | Change `"environment": "sandbox"` → `"production"`, paste production credentials | One-time per test site |
| Clear out the old sandbox tokens | Set `access_token`, `refresh_token`, and `realm_id` to `""` in the config | One-time |
| Register your redirect URI under the Production keys | In the Developer Portal → your app → Production → Redirect URIs — confirm `http://localhost:8000/callback` is listed | One-time |
| Run the OAuth flow | Run any NGAME script that calls `ensure_quickbooks_auth()` — your browser opens, the non-profit admin logs in and authorizes, tokens are saved automatically | One-time, then silent |
| Run NGAME normally | Training phase, dashboard, everything else — identical to your sandbox workflow | Ongoing |

---

### What Does NOT Change

| Thing | Status |
|---|---|
| Your Intuit Developer account | No changes needed — you already have one |
| NGAME codebase | No code changes needed |
| Your machine as the "Surveillance computer" | You're playing the FRP role — your machine is the surveillance computer for this test |
| The non-profit's QBO workflow | Nothing changes for the bookkeeper — they keep doing what they do |
| Intuit app review / certification | Not required yet — production apps can serve up to **25 companies** before Intuit's formal review is required. One non-profit is well within that limit |

---

### The One Gotcha to Watch

Intuit's OAuth consent screen will show your **app name** (whatever you named it in the Developer Portal) to the non-profit admin when they authorize. Make sure the app name is something recognizable and professional — e.g. "NGAME Financial Surveillance" — so they aren't confused by a generic or placeholder name when they click Authorize.

---

**User**

OK. That scenario--testing with a live non-profit who is willing to support my development. New another scenario: The School of Business in a university wants to incorporate NGAME into their practice lab. They will use QBO to set up fictitious non-profit companies on their own and completely from scratch: Chart of Accounts, donors.... everything. They will get their own QBO license directly from Intuit. Assume that NGAME can now be deployed commercially, based on successful field tests, such as the one whose guidance you provided above (the trusted site scenario).  My assumption is that a computer or a group of computers in that lab or a select group of students will each have an NGAME license and that NGAME willl be installed on those students' surveillance computers.  Same request to you: proved the same format of tables, explanations, and warnings as you have thus far.

---

**Cursor**

## University Business School Lab Deployment

### Context: What Makes This Scenario Different

There are three meaningful differences from the field-test scenario that cascade through everything else:

| Factor | Field Test | University Lab |
|---|---|---|
| Number of QBO companies | 1 | Many (one per student or team) |
| Who sets up QBO | Pre-existing organization | University builds from scratch |
| Intuit app scale | Under 25-company threshold | Likely exceeds it — full certification required |
| NGAME distribution | You install it manually | Packaged installer; students self-install |
| Your role | Developer acting as FRP | Software vendor; faculty/students are FRPs |

---

### What Ron Must Complete Before This Deployment

| Task | Details | Timing |
|---|---|---|
| Pass Intuit's production app review | Required once you exceed ~25 connected companies. Submit through the Developer Portal → App Assessment. Intuit reviews security practices, data handling, and UI. Timeline is typically 2–6 weeks. | Before launch |
| Finalize bundled credentials | `client_id` and `client_secret` must be embedded in the installer — never exposed to students | Before installer is built |
| Build a packaged installer | Students should run one installer (e.g. a `.pkg` for Mac or `.exe` for Windows) that installs Python environment, NGAME, dependencies, and pre-fills app credentials | Before launch |
| Establish a NGAME license model | Per-seat, per-company, or per-institution — the university buys one institutional license and distributes to students | Before launch |

---

### What the University Needs to Do

| Task | Details | Who Does It | Effort |
|---|---|---|---|
| Obtain QBO licenses | One QBO company file per student or team. Intuit has an **academic/educational program** — the university should contact Intuit directly to ask about volume academic pricing or the [Intuit Education Program](https://quickbooks.intuit.com/education/). This can significantly reduce per-seat cost. | Dept. administrator | One-time procurement |
| Build each fictitious company | Chart of Accounts, donor list, transaction history — this is the educational exercise itself. Each company should be set up to produce meaningful training data for NGAME. | Faculty / students | Ongoing (academic exercise) |
| Designate one QBO Admin per company | Each fictitious QBO company needs at least one user with Admin rights. For a student company, that student is the Admin. | Faculty | At company setup |
| Purchase an institutional NGAME license | One transaction with Ron; covers the full lab cohort | Dept. administrator | One-time procurement |
| Distribute NGAME installer to students | Standard IT distribution — shared drive, LMS download, or USB. No special configuration needed per student | IT / faculty | Per semester |

---

### What Each Student Needs to Do

| Task | Details | Effort |
|---|---|---|
| Install NGAME on their surveillance computer | Run the installer Ron provides. App credentials are already bundled — nothing to configure manually. | 5 minutes, one-time |
| Authorize NGAME against their QBO company | On first run, browser opens → student logs into their fictitious QBO company → clicks Authorize → done. Tokens save automatically. | 2 minutes, one-time |
| Run the training phase | Same as any FRP — establish baseline behavior from their company's transaction history | Per lab exercise |
| Monitor the dashboard | Watch for anomalies their classmates (playing the bookkeeper role) introduce | Ongoing during semester |

---

### The Bookkeeper / FRP Role Split in a Lab Context

This is worth calling out explicitly because the lab has a unique dynamic:

| Role | Who plays it | Machine |
|---|---|---|
| Bookkeeper | Student (or a designated "fraud actor" student) enters transactions in QBO from any machine — QBO is cloud-based, so any browser works | Any lab computer or personal laptop |
| FRP / NGAME operator | Same student (or a different student pair) runs NGAME on the Surveillance computer | The designated surveillance computer |

A common lab exercise structure: Student A plays the bookkeeper and introduces a hidden anomaly. Student B plays the FRP and tries to detect it using NGAME. Then they swap. Nothing about this requires any changes to NGAME.

---

### Faculty Supervision Option (Future Enhancement to Flag)

A faculty member may want a single dashboard that monitors **all** student companies simultaneously — one pane of glass across the whole lab. NGAME currently runs one company per installation. This is a meaningful product enhancement to plan for the academic market: a **multi-tenant faculty dashboard** that connects to N companies with N separate OAuth tokens. Not required for launch, but worth noting as a near-term roadmap item.

---

### Warnings and Gotchas

| Risk | Details |
|---|---|
| Intuit app certification timeline | Plan 6–8 weeks minimum before the semester starts. Do not assume it will be fast. |
| QBO Academic Program availability | Intuit's academic pricing has changed over the years. Confirm current terms directly with Intuit — do not promise the university a price point until you have it in writing. |
| Each company needs its own OAuth consent | There is no bulk authorization. Each student runs the consent flow once for their company. Faculty cannot pre-authorize on behalf of students. |
| Shared computers in a lab | If students share lab machines (not personal laptops), each `quickbooks_config.json` must be in a student-specific profile or directory. Otherwise Student B will overwrite Student A's tokens. Build this into the installer's directory structure. |
| QBO company must have enough transaction history | NGAME's training phase needs sufficient data to establish a meaningful baseline. A brand-new fictitious company will need a few weeks of simulated transactions before training produces useful z-scores. Build this into the lab timeline. |
| Refresh token expiration | Tokens expire after ~100 days of inactivity. If a company goes unused between semesters, students will need to re-authorize at the start of the next term. This is a 2-minute task but faculty should budget for it. |

---

**User**

Re population of a fictitious company's data, is it not possible to import directly a pre-built company via a QBB file, as with the old QB Desktop? I'm not a QBO expert. I only know what I did with QB Desktop in my former company. So this is a QB user's question.

---

**Cursor**

This is a QuickBooks product question, not a coding task, so no plan is needed — just a direct answer.

---

## QBB Files and QBO: The Short Answer

**No. QBO does not accept QBB files.** QBB is a QB Desktop backup format. QBO is an entirely separate product with a different data model, and Intuit has never bridged the two in that direction.

---

## What QBO Does Support for Pre-Populating a Company

| Method | What it covers | Practical for a university lab? |
|---|---|---|
| **CSV import** | Chart of Accounts, Customers, Vendors, Products/Services | Yes — faculty can build template CSV files once and students import them at company setup. This is the closest equivalent to "loading a starter company." |
| **IIF import** | Some transaction types (limited, legacy format) | Possible but finicky. Not recommended for a clean lab setup. |
| **Third-party import tools** (Transaction Pro, SaasAnt, etc.) | Full transaction history in bulk | Yes, but adds a paid tool and complexity. Overkill for a lab unless deep history is needed for NGAME training baseline. |
| **Intuit's Desktop-to-Online migration tool** | Full company migration from a real QBB file | Technically yes, but it's designed for one-time live migrations of real companies, not for cloning fictitious training companies. Intuit's terms likely prohibit using it as a lab template mechanism. |
| **QBO Sample Company** ("Craig's Design and Landscaping") | A pre-built Intuit-provided practice company | Good for exploration, but students cannot modify or own it, and it cannot be connected to NGAME via OAuth since it isn't a real company under the student's account. |
| **Manual entry** | Everything | Always works; time-consuming; is itself the accounting lab exercise |

---

## The Practical Recommendation for the Lab

The most realistic approach for the university scenario is a **faculty-maintained set of CSV import templates**:

- One CSV for Chart of Accounts (non-profit structure: program funds, restricted/unrestricted net assets, donor revenue accounts, etc.)
- One CSV for Vendors and Donors (fictitious names)
- A seed set of historical transactions imported via CSV or a tool like SaasAnt

Students import those templates at company setup — takes about 15 minutes — and the company is immediately meaningful enough for NGAME's training phase. Faculty maintains the templates as a versioned file that evolves with the curriculum.

This is worth flagging to the university's faculty contact early, because "set up a company from scratch" underestimates the setup time if they're expecting a QBB-style instant restore. The CSV template approach solves it neatly.

---

**User**

Very general marketing question for confirmation: NGAME is a self-contained application that accesses QBO accounts. The QBO never sees even a hint of NGAME in any screen. I maintain that NGAME is therefore not really a "QB Add-on" but a helper app.  My intention is that students pursuing a career in auditing will nevertheless develop a reliance on NGAME and will expect to incorporate into their professional "toolbox"

---

**Cursor**

Your characterization is technically accurate and the marketing positioning is sound. A few confirmations and one nuance worth knowing.

---

## NGAME's Relationship to QBO: Technical Reality

| Characteristic | Reality |
|---|---|
| Appears in QBO's daily interface | No — the bookkeeper never sees any trace of NGAME |
| Appears in QBO's App Store | No — NGAME is not listed there and does not need to be |
| Modifies QBO data in any way | No — NGAME is read-only. It queries; it never writes. |
| Runs inside QBO's environment | No — it runs entirely on the Surveillance computer |
| Is it a "QB Add-on"? | No, by any reasonable definition. It is an independent application that happens to use QBO as its data source. |

**The one nuance:** NGAME does appear in one obscure QBO location — the company's **Settings → Connected Apps** list. A QBO admin looking in that settings screen would see that "NGAME" (your app name) has been granted read access. This is a standard OAuth disclosure, not an integration. The bookkeeper doing daily work sees nothing. This is worth knowing but does not affect your positioning.

---

## The Right Analogy: ACL and IDEA

Your positioning maps precisely onto an already-established category in the auditing profession. Two well-known examples:

| Tool | What it does | Relationship to the accounting system |
|---|---|---|
| **ACL (Galvanize / Diligent)** | Data analytics for auditors — extracts and analyzes GL data | External. Never touches the accounting system's UI. Auditors consider it a core career skill. |
| **IDEA (CaseWare)** | Same category — fraud detection, transaction analysis | External. Taught in accounting programs globally. Students who learn it in school advocate for it professionally. |

NGAME belongs in exactly this category. The precedent is well-established: auditing software that runs alongside the accounting system, not inside it, and that practitioners learn as students and carry into their careers.

---

## Confirming the Career Toolbox Strategy

The educational market strategy you're describing has a proven track record in this space. ACL and IDEA built significant market share specifically through university accounting programs — students who trained on them as undergraduates became the staff auditors and eventually partners who specified those tools on every engagement. NGAME targeting auditing students as early adopters is not just reasonable; it is the textbook playbook for this category.

