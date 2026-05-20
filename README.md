# 📧 HR Email Automation Tool

> Personalised job-seeking emails to HR contacts — automated, tracked, and resumé-attached.

Built for job seekers who want to reach the right HR at the right company without spending hours copy-pasting emails manually.

\---

## ✨ Features

* 🎯 **Personalised emails** — uses HR's first name + company name in every email
* 📎 **Auto-attaches resume** — PDF attached to every email automatically
* 📊 **Tracks everything** — logs sent / failed / skipped to a CSV
* 🔁 **Resumes where it left off** — re-run safely, already-sent contacts are skipped
* ⏱️ **Rate limiting** — configurable delay between emails to avoid spam flags
* 🧪 **Dry run mode** — preview emails without sending anything
* ⚙️ **Zero code changes needed** — all personal details live in `config.yaml`

\---

## 📁 Folder Structure

```
hr\\\_outreach/
├── hr\\\_email\\\_automation.py   # main script — never needs editing
├── config.yaml              # YOUR details go here
├── hr\\\_contacts.csv          # HR contacts (Name, Email, Title, Company)
├── your\\\_resume.pdf          # your resume PDF
├── sent\\\_log.csv             # auto-generated — tracks sent emails
└── email\\\_run.log            # auto-generated — full run log
```

\---

## 🚀 Quick Start

### 1\. Install dependencies

```bash
pip install pandas pyyaml
```

### 2\. Fill in `config.yaml`

```yaml
email:
  gmail:        "your.email@gmail.com"
  app\\\_password: "xxxx xxxx xxxx xxxx"   # from myaccount.google.com/apppasswords

profile:
  name:     "Your Name"
  phone:    "+91-XXXXXXXXXX"
  email:    "your.professional@email.com"
  degree:   "M.Tech in Computer Science"
  college:  "IIT Bombay"
  gpa:      "9.0/10"
  linkedin: "https://linkedin.com/in/yourprofile"
  github:   "https://github.com/yourusername"

highlights:
  - "Your achievement 1"
  - "Your achievement 2"

settings:
  dry\\\_run: true    # set to false to actually send
```

### 3\. Prepare your HR contacts CSV

Your `hr\\\_contacts.csv` should have these columns:

```
Name, Email, Title, Company
Akanksha Puri, akanksha@company.com, Head HR, SourceFuse Technologies
```

### 4\. Dry run first (safe preview)

```bash
python hr\\\_email\\\_automation.py
```

You'll see 5 sample email subjects — no emails sent.

### 5\. Go live

Set `dry\\\_run: false` in `config.yaml`, then:

```bash
# Run safely in background (keeps going even if terminal closes)
nohup python hr\\\_email\\\_automation.py > output.log 2>\\\&1 \\\&

# Watch live progress
tail -f output.log
```

\---

## ⚙️ Gmail App Password Setup

1. Enable 2-Step Verification at [myaccount.google.com/security](https://myaccount.google.com/security)
2. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Create a new app password → name it `HR Mail`
4. Copy the 16-character password into `config.yaml`

> ⚠️ Use a \\\*\\\*personal Gmail\\\*\\\* only — institutional/work accounts block app passwords.

\---

## 📊 Tracking Results

After a run, check your log:

```bash
# Quick summary
grep -c "sent" sent\\\_log.csv
grep -c "failed" sent\\\_log.csv

# Full log
cat sent\\\_log.csv
```

**Bounce-backs** (invalid email addresses) will appear in your Gmail inbox as
`Delivery Status Notification (Failure)` — subtract these from sent count for real deliveries.

\---

## 🔒 Security \& .gitignore

Never commit credentials. Your `.gitignore` should include:

```
config.yaml
sent\\\_log.csv
email\\\_run.log
\\\*.pdf
.env
```

Share only `hr\\\_email\\\_automation.py`, `config.yaml` (with blank values), and `README.md`.

\---

## 📬 Gmail Sending Limits

|Account Type|Daily Limit|Recommended Setting|
|-|-|-|
|Free Gmail|500/day|`daily\\\_limit: 80`|
|Google Workspace|2000/day|`daily\\\_limit: 150`|

Default delay is 30 seconds between emails — keeps you well under spam thresholds.

\---

## 🤝 Contributing

PRs welcome! Ideas for improvement:

* \[ ] Bounce-back auto-detection
* \[ ] HTML email preview in browser before sending
* \[ ] LinkedIn InMail version
* \[ ] Multiple email template support

\---

## 📄 License

MIT — free to use, modify, and share.

\---

*Built with ❤️ for job seekers. Happy hunting!*

