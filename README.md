<div align="center">

# 🦈 Sharky TikTok Automation Suite

### by [SharkySolvers](https://github.com/sharkysolvers)

**Automate your TikTok growth — views, likes, comments, follows — all from one clean CLI.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Selenium](https://img.shields.io/badge/Selenium-4.20%2B-43B02A?style=for-the-badge&logo=selenium&logoColor=white)](https://selenium.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://www.microsoft.com/windows)

---

![Sharky Banner](https://img.shields.io/badge/🦈_SHARKY-TikTok_Automation-FF0050?style=for-the-badge&labelColor=000000)

</div>

---

## ⚡ What Is This?

Sharky is a **TikTok automation toolkit** that lets you boost engagement on any TikTok video or profile. Load your accounts (or use browser cookies), pick a target, and let the bots run.

| Tool | What It Does |
|------|-------------|
| 🔑 **Account Loader** | Import/manage TikTok accounts or cookie sessions |
| 👀 **View Bot** | Multi-threaded video views with randomized watch durations |
| ❤️ **Like Bot** | Mass-like any video using accounts or cookie session |
| 💬 **Comment Bot** | Post randomized or custom comments at scale |
| 👥 **Follow Bot** | Mass-follow any profile from your account pool |

---

## 📁 File Structure

```
sharky/
├── main.py                     # Interactive menu launcher
├── run.bat                     # One-click Windows launcher
├── input/                      # Your files go here
│   ├── accounts.txt            # Your TikTok accounts (user:pass:email)
│   ├── cookies.json            # TikTok cookie export (optional)
│   └── proxies.txt             # Your proxies (optional)
├── output/                     # Generated at runtime
│   ├── accounts.txt            # Loaded/imported accounts
│   ├── settings.json           # Saved settings
│   └── automation.log          # Activity logs
└── scripts/
    ├── config.py               # All settings & tunables
    ├── utils.py                # Shared utilities & browser factory
    ├── accountloader.py        # Account management tool
    ├── viewbot.py              # View bot
    ├── likebot.py              # Like bot
    ├── commentbot.py           # Comment bot
    ├── followbot.py            # Follow bot
    └── requirements.txt        # Python dependencies
```

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/sharkysolvers/sharky-tiktok.git
cd sharky-tiktok
```

### 2. Run it

**Windows — double-click `run.bat`** and you're in. It handles venv creation and dependency installation automatically.

**Manual setup:**

```bash
python -m venv venv
venv\Scripts\activate
pip install -r scripts\requirements.txt
python main.py
```

### 3. Load your accounts

You have **two options** for authentication:

#### Option A: Username/Password accounts

Add accounts to `input/accounts.txt` in one of these formats:

```
username:password
username:password:email
email:password
```

Then select **[1] Account Loader** → **[3] Import from file** in the menu.

#### Option B: Cookie login (recommended)

Export your TikTok cookies from your browser using an extension like [EditThisCookie](https://www.editthiscookie.com/) or [Cookie-Editor](https://cookie-editor.cgagnier.ca/). Save the export as `input/cookies.json`.

The cookie file should be a JSON array of cookie objects:

```json
[
  {
    "domain": ".tiktok.com",
    "name": "sessionid",
    "value": "your_session_id_here",
    "path": "/",
    "secure": true,
    "httpOnly": true,
    "expirationDate": 1798453173
  }
]
```

The key cookie is `sessionid` — without it, cookie login won't work.

**Manage cookies from the menu:** Account Loader → **[4] Cookie status**, **[5] Import cookie file**, **[6] Clear cookie file**.

When cookies are loaded and no `accounts.txt` exists, all bots automatically use the cookie session — no password login needed.

### 4. Pick a bot and run

Select any bot from the menu, paste your target TikTok URL, set how many actions you want, and let it cook.

---

## ⚙️ Settings

Access settings from the main menu with **[6] Settings**. Toggles are saved to `output/settings.json` and persist between sessions.

| Setting | Default | Description |
|---------|---------|-------------|
| **Headless Mode** | `ON` | Run browsers without visible GUI |
| **Use Proxies** | `OFF` | Route traffic through proxies |

### Proxy Setup

1. Set **Use Proxies → ON** in settings
2. Create `input/proxies.txt` with one proxy per line:

```
ip:port
username:password@ip:port
```

---

## 🔧 Configuration

All tunables live in [`scripts/config.py`](scripts/config.py):

| Parameter | Default | What It Controls |
|-----------|---------|-----------------| 
| `MIN_ACTION_DELAY` | `2.0s` | Minimum delay between actions |
| `MAX_ACTION_DELAY` | `5.0s` | Maximum delay between actions |
| `BATCH_SIZE` | `10` | Actions per batch before pause |
| `BATCH_PAUSE_MIN` | `15.0s` | Minimum batch pause |
| `BATCH_PAUSE_MAX` | `30.0s` | Maximum batch pause |
| `VIEW_DURATION_MIN` | `5s` | Minimum video watch time |
| `VIEW_DURATION_MAX` | `15s` | Maximum video watch time |
| `COMMENT_POOL` | 20 comments | Randomized comment selection |

---

## 🛡️ Anti-Detection Features

- **Randomized User-Agents** — fresh UA per browser session
- **WebDriver flag removal** — patches `navigator.webdriver` detection
- **Human-like delays** — randomized with jitter, no fixed intervals
- **Batch pausing** — longer cooldowns between batches to avoid rate limits
- **Proxy rotation** — distribute requests across multiple IPs
- **Staggered launches** — view bot staggers browser spawns to avoid spikes

---

## 🍪 Cookie Login

Cookie-based login bypasses TikTok's password flow entirely — no CAPTCHA, no 2FA, no rate-limited login attempts. Just a valid browser session injected directly.

**How it works:**
1. `create_browser()` loads cookies from `input/cookies.json` on every browser launch
2. `login_account()` checks if the cookie session is already valid before attempting password login
3. If the session is active, password login is skipped entirely
4. If cookies are expired/invalid, it falls back to password login

**Session expiry:** Check your cookie status via Account Loader → **[4]** to see when your session expires. Re-export cookies from your browser when they expire.

---

## 📋 Requirements

- **Python 3.10+**
- **Google Chrome** installed
- **Windows** (Linux/Mac untested but should work with minor tweaks)

### Dependencies

```
selenium>=4.20.0
webdriver-manager>=4.0.1
fake-useragent>=1.5.1
colorama>=0.4.6
```

---

## ⚠️ Disclaimer

This tool is provided for **educational and research purposes only**. Automated interaction with TikTok may violate their [Terms of Service](https://www.tiktok.com/legal/terms-of-service). Use at your own risk. The developers are not responsible for any account bans, restrictions, or other consequences resulting from the use of this software.

---

## 📝 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built by [SharkySolvers](https://github.com/sharkysolvers)** 🦈

</div>
