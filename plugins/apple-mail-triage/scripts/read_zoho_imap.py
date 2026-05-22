#!/usr/bin/env python3
"""
read_zoho_imap.py - Legge email Zoho via IMAP per account NON configurati in Apple Mail.

Per account Zoho già in Apple Mail (es. elha@bitcoinpeople.it), usa lo script
AppleScript read_mail.applescript: Apple Mail già parla IMAP con Zoho.

Usage:
    python3 read_zoho_imap.py [--limit N] [--unread-only true|false]

Credenziali via env var o file ~/.zoho_mail_creds (JSON):
    {
        "email": "you@yourdomain.com",
        "app_password": "xxxx-xxxx-xxxx",
        "server": "imap.zoho.eu"
    }

App password si genera su:
    EU: https://accounts.zoho.eu/home#security/app-passwords
    US: https://accounts.zoho.com/home#security/app-passwords

Output: JSON array compatibile con read_mail.applescript (stessi campi).
"""

import argparse
import email
import email.policy
import imaplib
import json
import os
import re
import sys
from email.header import decode_header
from pathlib import Path


def load_creds():
    creds_file = Path.home() / ".zoho_mail_creds"
    if creds_file.exists():
        with creds_file.open() as f:
            return json.load(f)
    env_email = os.environ.get("ZOHO_EMAIL")
    env_pw = os.environ.get("ZOHO_APP_PASSWORD")
    env_server = os.environ.get("ZOHO_IMAP_SERVER", "imap.zoho.eu")
    if env_email and env_pw:
        return {"email": env_email, "app_password": env_pw, "server": env_server}
    sys.stderr.write(
        "ERROR: nessuna credenziale. Crea ~/.zoho_mail_creds o esporta "
        "ZOHO_EMAIL e ZOHO_APP_PASSWORD.\n"
    )
    sys.exit(2)


def decode_field(raw):
    if raw is None:
        return ""
    parts = decode_header(raw)
    out = []
    for text, enc in parts:
        if isinstance(text, bytes):
            try:
                out.append(text.decode(enc or "utf-8", errors="replace"))
            except LookupError:
                out.append(text.decode("utf-8", errors="replace"))
        else:
            out.append(text)
    return "".join(out)


def get_snippet(msg, limit=300):
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                try:
                    body = part.get_content()
                    break
                except Exception:
                    continue
        if not body:
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    try:
                        body = re.sub(r"<[^>]+>", " ", part.get_content())
                        break
                    except Exception:
                        continue
    else:
        try:
            body = msg.get_content()
        except Exception:
            body = ""
    body = re.sub(r"\s+", " ", body).strip()
    return body[:limit]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--unread-only", default="true", choices=["true", "false"])
    p.add_argument("--folder", default="INBOX")
    args = p.parse_args()

    creds = load_creds()
    unread_only = args.unread_only == "true"

    try:
        m = imaplib.IMAP4_SSL(creds["server"])
        m.login(creds["email"], creds["app_password"])
    except Exception as e:
        sys.stderr.write(f"ERROR: login fallito: {e}\n")
        sys.exit(3)

    m.select(args.folder, readonly=True)
    criterion = "UNSEEN" if unread_only else "ALL"
    typ, data = m.search(None, criterion)
    if typ != "OK":
        sys.stderr.write(f"ERROR: search fallita: {typ}\n")
        sys.exit(4)

    ids = data[0].split()
    ids = ids[-args.limit:][::-1] if ids else []

    results = []
    for msg_id in ids:
        typ, data = m.fetch(msg_id, "(RFC822)")
        if typ != "OK":
            continue
        msg = email.message_from_bytes(data[0][1], policy=email.policy.default)
        results.append({
            "id": decode_field(msg.get("Message-ID", "")).strip("<>"),
            "account": creds["email"],
            "sender": decode_field(msg.get("From", "")),
            "subject": decode_field(msg.get("Subject", "")),
            "date": decode_field(msg.get("Date", "")),
            "read": not unread_only,
            "snippet": get_snippet(msg),
        })

    m.logout()
    print(json.dumps(results, ensure_ascii=False))


if __name__ == "__main__":
    main()
