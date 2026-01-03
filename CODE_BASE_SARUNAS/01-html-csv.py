from html import unescape
from pathlib import Path
import csv
import re


input_path = Path(r"C:\Users\JurisFedotovs\Desktop\RTU\MASTER\Āgenskalna_klīnika_sarunas\EXPERIMENT\CODE_BASE\MESSAGES")

##### Allowed authors (others -> anonymized) #####
ALLOWED_AUTHORS = {"Āgenskalna klīnika", "Edgars Mednis"}

##### Regular expressions patterns #####
RE_MSG_START = re.compile(r'<div class="message[^"]*" id="([^"]+)"')
RE_TIMESTAMP = re.compile(r'<div class="pull_right date details" title="([^"]+)"')
RE_FROM = re.compile(r'<div class="from_name"[^>]*>(.*?)</div>', re.DOTALL)
RE_REPLY = re.compile(r'<div class="reply_to details">.*?GoToMessage\((\d+)\)', re.DOTALL)
RE_TEXT = re.compile(r'<div class="text"[^>]*>(.*?)</div>', re.DOTALL)

def clean_html(s):
    """Remove HTML tags and unescape HTML entities."""
    s = re.sub(r'<[^>]*>', '', s)
    return unescape(s).strip()

def parse_file(filepath, last_sender=None):
    """Parse one Telegram messages*.html file."""
    with open(filepath, encoding="utf-8", errors="replace") as f:
        content = f.read()

    blocks = content.split('<div class="message')
    messages = []

    for block in blocks:
        if 'id=' not in block:
            continue

        block = '<div class="message' + block

        msg_id = None
        timestamp = None
        sender = None
        reply = None
        text = None

        ##### Message ID #####
        m = RE_MSG_START.search(block)
        if m:
            msg_id = m.group(1).replace("message", "")

        ##### Timestamp #####
        t = RE_TIMESTAMP.search(block)
        if t:
            ts = t.group(1)
            timestamp = " ".join(ts.split()[:2])  

        ##### Sender #####
        s = RE_FROM.search(block)
        if s:
            sender = clean_html(s.group(1))
            last_sender = sender
        else:
            sender = last_sender if last_sender else "User"

        ##### Anonymize sender if not Āgenskalna klīnika or Edgars Mednis #####
        if sender not in ALLOWED_AUTHORS:
            sender = "User"

        ##### Reply #####
        r = RE_REPLY.search(block)
        if r:
            reply = r.group(1)

        ##### Message content #####
        txt = RE_TEXT.search(block)
        if txt:
            text = clean_html(txt.group(1))
        else:
            text = ""

        messages.append((msg_id, timestamp, sender, reply, text))

    return messages, last_sender

##### Main function #####
def main():
    all_messages = []
    last_sender = None

    for p in input_path.iterdir():
        if p.suffix.lower() in (".html", ".htm") and p.name.startswith("messages"):
            print(f"Parsing file: {p.name}")
            msgs, last_sender = parse_file(p, last_sender)
            all_messages.extend(msgs)

    if not all_messages:
        print("No messages found.")
        return

    ##### Output CSV file path #####
    out_file = Path(r"C:\Users\JurisFedotovs\Desktop\RTU\MASTER\Āgenskalna_klīnika_sarunas\EXPERIMENT\CODE_BASE\DATA\01_anonymized_messages.csv")


    with open(out_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "timestamp", "sender", "reply_to", "content"])
        for msg in all_messages:
            writer.writerow(msg)

    print(f"\nSaved anonymized CSV to:\n{out_file}")
    print(f"Total messages parsed: {len(all_messages)}")

##### Main entry #####
if __name__ == "__main__":
    main()
print("DONE")