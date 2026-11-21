# NGAME — ngrok cookbook (Production OAuth tunnel)

**Audience:** Technical consultant on the **surveillance PC**.  
**When:** Track B (live QuickBooks Online). Intuit Production redirect URIs must be **https**; `localhost` is not allowed.

**Not for:** The FRP or the bookkeeper. ngrok is not installed on the bookkeeper PC.

**Related:** [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) Track B **B3–B4**. Registering the URI on the Intuit app is **Audithentic owner** work, not this file. The installer only starts the tunnel and puts the matching `https://…/callback` string in `quickbooks_config.json`.

ngrok is **not** bundled with NGAME. The tunnel is needed only for the one-time Connect click. After tokens exist, stop ngrok. Daily FRP use is local token refresh.

---

## Checklist

- [ ] This is the surveillance PC (Windows PowerShell or macOS Terminal)
- [ ] Port **8000** will be free when you start the tunnel (NGAME’s OAuth callback)
- [ ] You have (or will create) a **free ngrok account** — not an Intuit account
- [ ] A **second** window will run `python run_data_extraction.py` while this tunnel stays up

---

## N1 — Install ngrok (once per PC)

**Windows PowerShell:**

```powershell
winget install ngrok -s msstore
```

**Then close this PowerShell window completely and open a new PowerShell window.** The window that ran `winget` does **not** pick up ngrok on PATH. `ngrok` is not recognized until you start a fresh session.

In the **new** window:

```powershell
ngrok version
```

If `winget` is unavailable, install from [ngrok.com/download/windows](https://ngrok.com/download/windows), then close and reopen PowerShell the same way.

**macOS:** `brew install ngrok/ngrok/ngrok`, then open a **new** Terminal window and run `ngrok version`.

---

## N2 — Authenticate ngrok (once per PC)

`ngrok http 8000` **before** an authtoken is saved fails with **authentication failed** / **session not authenticated** / **requires an account and a valid credential**. That is expected.

1. Sign up for a free account at [ngrok.com](https://ngrok.com) (or sign in). This is **not** Intuit.
2. Copy the authtoken from [dashboard.ngrok.com/get-started/your-authtoken](https://dashboard.ngrok.com/get-started/your-authtoken).
3. In the **new** PowerShell/Terminal window:

```powershell
ngrok config add-authtoken "YOUR_AUTHTOKEN"
```

Replace `YOUR_AUTHTOKEN` with the dashboard token (keep the quotes). Success: **Authtoken saved**. You do this once per PC.

---

## N3 — Start the tunnel

Leave this window **open** until OAuth completes (Track B **B4**). Do **not** type an https URL at the prompt.

```powershell
ngrok http 8000
```

**The tunnel is running only if** the ngrok status panel is showing (including **Forwarding**) and you are **not** back at a `PS …>` or shell prompt.

From **Forwarding**, copy the **https** base URL (for example `https://abcd1234.ngrok-free.app` or `https://….ngrok-free.dev`). Use **https**, not http. Placeholders such as `<random>` in other docs are not something you type.

The value you will use in `quickbooks_config.json` is that host **plus** `/callback`:

```text
https://abcd1234.ngrok-free.app/callback
```

Do not omit `/callback`. Do not add a trailing slash after `callback`. Copy the hostname **character for character** from ngrok (including the `n` in `ngrok`).

Free ngrok often **reuses** the same host the next day. If Forwarding matches the JSON and the URI already registered on the app, do **not** force a new URL. If you close ngrok overnight, start `ngrok http 8000` again; if the host **changed**, JSON (and the owner-registered URI) must be updated before B4.

---

## N4 — What the installer does vs what the owner does

| Who | Action |
|-----|--------|
| **Installer** | N1–N3. Set `redirect_uri` in `quickbooks_config.json` to `https://(Forwarding host)/callback`. Run B4 in a **second** window. |
| **Audithentic owner** | That exact string must already be on the Intuit app **Production** Redirect URIs. The installer does **not** sign in at developer.intuit.com. |

If the live Forwarding host is **not** the URI in the install pack, **stop**. Ask Audithentic to register the new `https://…/callback` (or, if you are the owner doing a rehearsal, use the local owner appendix). Do not invent a developer.intuit.com login.

---

## N5 — During OAuth (B4)

Keep the ngrok window as it is. In a **second** PowerShell/Terminal (repo root, **venv active**):

```powershell
.venv\Scripts\Activate.ps1
python run_data_extraction.py
```

(macOS: `source .venv/bin/activate` then `python3 run_data_extraction.py`.)

The callback listener on port **8000** lasts about **three minutes**. Connect and finish the browser flow in that window. If you wander into other Intuit pages first, the listener dies; ngrok then shows **502** / **connection refused** / **upstream … localhost:8000**.

**ngrok “You are about to visit …” / Visit Site:** expected on the free tier. Click **Visit Site** so the callback reaches NGAME.

**Success:** browser shows **NGAME: OAuth complete. You can close this tab.** ngrok may log **200** then **502**. The 502 is a second hit after NGAME closed port 8000 — not a failed OAuth. Stop ngrok (**Ctrl+C**). Confirm `access_token`, `refresh_token`, and `realm_id` are non-empty in `quickbooks_config.json`.

---

## Troubleshooting

| Symptom | Action |
|---------|--------|
| `ngrok` is not recognized | N1. **Close** PowerShell/Terminal and open a **new** one, then `ngrok version` |
| authentication failed / session not authenticated | N2, then `ngrok http 8000` |
| `https://…` is not recognized as a cmdlet | That URL is not a command. Run `ngrok http 8000` and **copy** Forwarding |
| Looking at old Forwarding text but `PS …>` is back | Tunnel is **not** running. Run `ngrok http 8000` again |
| 502 / connection refused on Visit Site | Python listener timed out or exited. Re-run `run_data_extraction.py` with ngrok still up; Connect immediately |
| 200 then 502 after “OAuth complete” | Success. Stop ngrok |
| `redirect_uri` query parameter is invalid | JSON/browser URI must match the **Production** list for the **Production** Client ID (not Development keys). Owner registers the URI |
| Overnight / new host | New `ngrok http 8000` → if host changed, update JSON and wait for owner to register it before B4 |
