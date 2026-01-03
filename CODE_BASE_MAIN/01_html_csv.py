from html import unescape
from time import time
from pathlib import Path
import csv
import os
import re
import sys

FOLDERS = [
    Path(__file__).parent / "MESSAGES"
]

TARGET_SENDER = "Āgenskalna klīnika"

class Message:
    def __init__(self):
        self.message_id = None
        self.timestamp = None
        self.sender = None
        self.fwd = None
        self.reply = None
        self.content = None

    def toTuple(self):
        if self.message_id: self.message_id = self.message_id.replace('message', '')
        if self.timestamp: self.timestamp = ' '.join(self.timestamp.split()[:2])
        if self.sender: self.sender = unescape(self.sender.strip())
        if self.fwd: self.fwd = unescape(self.fwd.strip())
        if self.reply: self.reply = self.reply.replace('message', '')
        if self.content: self.content = unescape(self.content.strip())
        return (self.message_id, self.timestamp, self.sender, self.fwd, self.reply, self.content)

##### Regular expressions patterns ######
message_id_new_pattern = re.compile(r'<div class="message default clearfix" id="([^"]+)')
message_id_joined_pattern = re.compile(r'<div class="message default clearfix joined" id="([^"]+)')
timestamp_pattern = re.compile(r'<div class="pull_right date details" title="([^"]+)"')
fwd_pattern = re.compile(r'<div class="userpic userpic\d+" style="width: 42px; height: 42px">')
fwd_reply_pattern = re.compile(r'<div class="reply_to details">')
fwd_sender_pattern = re.compile(r'([^<]+)<span class="date details')
same_fwd_media_pattern = re.compile(r'<div class="media_wrap clearfix">')
same_fwd_text_pattern = re.compile(r'<div class="text">')
reply_pattern = re.compile(r'In reply to <a href="(?:messages\d*.html)?#go_to_([^"]+)"')

photo_pattern = re.compile(r'<div class="media clearfix pull_left media_photo">')
video_pattern = re.compile(r'<div class="media clearfix pull_left media_video">')
voice_pattern = re.compile(r'<div class="media clearfix pull_left media_voice_message">')
audio_pattern = re.compile(r'<div class="media clearfix pull_left media_audio_file">')
file_pattern = re.compile(r'<div class="media clearfix pull_left media_file">')
contact_pattern = re.compile(r'<div class="media clearfix pull_left media_contact">')
contact_link_pattern = re.compile(r'<a class="media clearfix pull_left block_link media_contact" href="[^"]+"')
location_link_pattern = re.compile(r'<a class="media clearfix pull_left block_link media_location" href="[^"]+"')
call_pattern = re.compile(r'<div class="media clearfix pull_left media_call( success)?">')
poll_pattern = re.compile(r'<div class="media_poll">')
game_pattern = re.compile(r'<a class="media clearfix pull_left block_link media_game" href="[^"]+">')

html_link_pattern = re.compile(r'</?a[^<]*>')
html_span_pattern = re.compile(r'</?span[^<]*>')
html_tags = ['em', 'strong', 'code', 'pre', 's']


def parse_folder(folder: Path):
    """Parse all Telegram export HTML files in a folder."""
    if not folder.exists():
        print(f"Folder not found: {folder}")
        return []

    os.chdir(str(folder))
    message_files = sorted(
        [p.name for p in folder.iterdir()
         if p.is_file() and p.suffix.lower() in ('.html', '.htm') and p.name.startswith("messages")]
    )

    if not message_files:
        print(f"⚠️ No message files in {folder}")
        return []

    print(f"📂 Parsing {len(message_files)} file(s) in {folder.name}")

    ##### Read all lines #####
    lines = []
    for file in message_files:
        with open(file, encoding='utf-8', errors='replace') as f:
            lines += [line.replace('\n', '').strip() for line in f if line.strip()]

    messages = []
    cur = 0
    last_sender = None
    last_fwd_sender = None

    while cur < len(lines):
        if not lines[cur].startswith('<div class='):
            cur += 1
            continue

        new = True
        message_id = re.findall(message_id_new_pattern, lines[cur])
        if not message_id:
            new = False
            message_id = re.findall(message_id_joined_pattern, lines[cur])
        if not message_id:
            cur += 1
            continue

        m = Message()
        m.message_id = message_id[0]

        if new:
            if cur + 4 < len(lines) and lines[cur + 4] == '</div>':
                cur += 8
            else:
                cur += 9
            timestamp = re.findall(timestamp_pattern, lines[cur]) if cur < len(lines) else None
            m.timestamp = timestamp[0] if timestamp else None
            cur += 4
            m.sender = lines[cur] if cur < len(lines) else None
            last_sender = m.sender
            cur += 3
            m.content = lines[cur] if cur < len(lines) else ''
        else:
            cur += 2
            timestamp = re.findall(timestamp_pattern, lines[cur]) if cur < len(lines) else None
            m.timestamp = timestamp[0] if timestamp else None
            m.sender = last_sender
            cur += 4
            m.content = lines[cur] if cur < len(lines) else ''

        if m.sender:
            m.sender = re.sub(r'<[^>]+>', '', m.sender).strip()

        if m.content:
            m.content = re.sub(r'<[^>]+>', '', m.content).strip()

        if m.sender == TARGET_SENDER:
            messages.append(m)

        cur += 1

    print(f"Extracted {len(messages)} messages from {folder.name} (sender: {TARGET_SENDER})")
    return messages


def main():
    t0 = time()
    all_messages = []

    for folder in FOLDERS:
        parsed = parse_folder(folder)
        all_messages.extend(parsed)

    if not all_messages:
        print("No messages found for the specified sender.")
        return

    output_path = Path(__file__).parent / "DATA" / f"01_Telegram-{TARGET_SENDER.replace(' ', '_')}-main.csv"
    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(list(all_messages[0].__dict__.keys()))
        writer.writerows([m.toTuple() for m in all_messages])

    print(f"Written filtered CSV to:\n{output_path}")
    print(f"Completed in {(time() - t0):.2f}s.")

if __name__ == "__main__":
    main()
print("DONE")