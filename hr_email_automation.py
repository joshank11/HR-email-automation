"""
HR Email Automation Script
==========================
Sends personalised job-seeking emails to HR contacts from a CSV.

HOW TO USE:
1. pip install pandas pyyaml
2. Fill in config.yaml with your details (no changes needed here)
3. Place your resume PDF in this folder
4. Run: python hr_email_automation.py

Author: github.com/joshank11
"""

import smtplib
import pandas as pd
import time
import logging
import os
import csv
import yaml
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime


# ─────────────────────────────────────────────
# LOAD CONFIG
# ─────────────────────────────────────────────
def load_config(path: str = "config.yaml") -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(
            "config.yaml not found! Copy config.yaml to this folder and fill in your details."
        )
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ─────────────────────────────────────────────
# EMAIL TEMPLATE — built entirely from config
# ─────────────────────────────────────────────
def build_email(cfg: dict, name: str, title: str, company: str) -> tuple[str, str]:
    p = cfg["profile"]
    j = cfg["job"]
    first_name = name.strip().split()[0]

    subject = f"Exploring Opportunities at {company} — {p['name']} ({p['college']})"

    bullets = "".join(f"<li>{h}</li>" for h in cfg.get("highlights", []))

    body = f"""
<html>
<body style="font-family: Arial, sans-serif; font-size: 14px;
             line-height: 1.7; color: #333; max-width: 600px;">

<p>Hi {first_name},</p>

<p>I hope this message finds you well. I am <strong>{p['name']}</strong>, an AI and Data
professional with a <strong>{p['degree']}</strong> from <strong>{p['college']}
(GPA: {p['gpa']})</strong> and {p['experience']} of hands-on experience building
production-grade data systems and GenAI workflows.</p>

<p>I am currently exploring new opportunities and believe my profile could be a strong
fit for AI/Data/GenAI roles at <strong>{company}</strong>.</p>

<p><strong>A quick snapshot of what I bring:</strong></p>
<ul>
{bullets}
</ul>

<p>I am open to roles such as <strong>{j['roles']}</strong>. My expected CTC is
<strong>{j['ctc']}</strong>, negotiable based on the role and responsibilities.</p>

<p>I have attached my resume for your reference. I would love a brief 15-minute
conversation if there are any relevant openings or if you foresee a fit in the
near future.</p>

<p>Thank you for your time, {first_name}. Looking forward to hearing from you.</p>

<p>Warm regards,<br>
<strong>{p['name']}</strong><br>
{p['degree']} — {p['college']}<br>
📧 {p['email']}<br>
📱 {p['phone']}<br>
🔗 <a href="{p['linkedin']}" style="color: #0073b1;">LinkedIn</a>
&nbsp;|&nbsp;
<a href="{p['github']}" style="color: #333;">GitHub</a>
</p>

</body>
</html>
"""
    return subject, body


# ─────────────────────────────────────────────
# CORE FUNCTIONS
# ─────────────────────────────────────────────
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)s  %(message)s",
        handlers=[
            logging.FileHandler("email_run.log"),
            logging.StreamHandler(),
        ],
    )


def load_contacts(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df.columns = [c.strip() for c in df.columns]
    before = len(df)
    df = df.dropna(subset=["Email"])
    df["Email"] = df["Email"].str.strip()
    df = df[df["Email"].str.contains("@")]
    logging.info(
        f"Loaded {len(df)} valid contacts "
        f"(dropped {before - len(df)} with missing/bad emails)"
    )
    return df


def skip_already_sent(df: pd.DataFrame, log_csv: str) -> pd.DataFrame:
    if not os.path.exists(log_csv):
        return df
    sent = pd.read_csv(log_csv)
    sent_emails = set(sent[sent["status"] == "sent"]["email"].str.lower())
    before = len(df)
    df = df[~df["Email"].str.lower().isin(sent_emails)]
    logging.info(f"Skipping {before - len(df)} already-sent contacts")
    return df


def log_result(log_csv, name, email, company, status, note=""):
    file_exists = os.path.exists(log_csv)
    with open(log_csv, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "name", "email", "company", "status", "note"])
        writer.writerow([datetime.now().isoformat(), name, email, company, status, note])


def send_email(smtp, from_addr, to_addr, cfg, name, title, company, resume_path):
    subject, html_body = build_email(cfg, name, title, company)
    p = cfg["profile"]

    msg = MIMEMultipart("mixed")
    msg["From"] = f"{p['name']} <{from_addr}>"
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))

    resume_display_name = f"{p['name'].replace(' ', '_')}_Resume.pdf"
    with open(resume_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f'attachment; filename="{resume_display_name}"')
    msg.attach(part)

    smtp.sendmail(from_addr, to_addr, msg.as_string())


def print_summary(log_csv: str):
    if not os.path.exists(log_csv):
        return
    df = pd.read_csv(log_csv)
    sent   = len(df[df["status"] == "sent"])
    failed = len(df[df["status"] == "failed"])
    logging.info("─" * 45)
    logging.info(f"  TOTAL PROCESSED : {len(df)}")
    logging.info(f"  ✓ SENT          : {sent}")
    logging.info(f"  ✗ FAILED        : {failed}")
    logging.info(f"  📋 LOG FILE     : {log_csv}")
    logging.info("─" * 45)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    setup_logging()

    try:
        cfg = load_config("config.yaml")
    except FileNotFoundError as e:
        logging.error(str(e))
        return

    s           = cfg["settings"]
    resume_path = cfg["resume"]["filename"]

    if not os.path.exists(resume_path):
        logging.error(
            f"Resume not found: '{resume_path}' — "
            f"place your PDF here and update config.yaml"
        )
        return

    df = load_contacts(s["csv_path"])
    df = skip_already_sent(df, s["log_csv"])

    if df.empty:
        logging.info("No new contacts to email. All done!")
        print_summary(s["log_csv"])
        return

    total = min(len(df), s["daily_limit"])
    logging.info(f"Will process {total} contacts. dry_run={s['dry_run']}")

    if s["dry_run"]:
        logging.info("=== DRY RUN — no emails will be sent ===")
        for _, row in df.head(5).iterrows():
            subj, _ = build_email(cfg, row["Name"], row.get("Title", ""), row["Company"])
            logging.info(f"  PREVIEW → {row['Email']} | Subject: {subj}")
        logging.info("Set dry_run: false in config.yaml to send for real.")
        return

    logging.info("Connecting to Gmail SMTP...")
    try:
        smtp = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        smtp.login(cfg["email"]["gmail"], cfg["email"]["app_password"])
        logging.info("Connected ✓")
    except Exception as e:
        logging.error(f"SMTP login failed: {e}")
        return

    sent_count = failed_count = 0

    for i, (_, row) in enumerate(df.head(total).iterrows()):
        name    = str(row.get("Name", "")).strip()
        email   = str(row.get("Email", "")).strip()
        title   = str(row.get("Title", "")).strip()
        company = str(row.get("Company", "")).strip()

        try:
            send_email(smtp, cfg["email"]["gmail"], email,
                       cfg, name, title, company, resume_path)
            logging.info(f"[{i+1}/{total}] ✓ Sent → {name} <{email}> at {company}")
            log_result(s["log_csv"], name, email, company, "sent")
            sent_count += 1
        except Exception as e:
            logging.warning(f"[{i+1}/{total}] ✗ Failed → {email}: {e}")
            log_result(s["log_csv"], name, email, company, "failed", str(e))
            failed_count += 1

        if i < total - 1:
            time.sleep(s["delay_seconds"])

    smtp.quit()
    logging.info(f"\n=== Done. Sent: {sent_count} | Failed: {failed_count} ===")
    print_summary(s["log_csv"])


if __name__ == "__main__":
    main()
