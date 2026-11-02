import sys
import subprocess
import json
import os
import shutil
import re

sys.stdout.reconfigure(encoding='utf-8')

video_map = [
    {
        "channel_group": "INDIAN CHANNEL",
        "channel_name": "Dhruv Rathee",
        "srt_file": "18M IN 1MONTH.srt",
        "video_id": "q678XLOueN8"
    },
    {
        "channel_group": "INDIAN CHANNEL",
        "channel_name": "Dhruv Rathee",
        "srt_file": "24M VIEWS IN 3WEEK.srt",
        "video_id": "vzlK59IG5K4"
    },
    {
        "channel_group": "INDIAN CHANNEL",
        "channel_name": "Max cro",
        "srt_file": "1.9M IN 1MONTH.srt",
        "video_id": "bqb1pKoJEok"
    },
    {
        "channel_group": "INDIAN CHANNEL",
        "channel_name": "Max cro",
        "srt_file": "16K IN 9DAYS.srt",
        "video_id": "Iv3Kl7N4zIk"
    },
    {
        "channel_group": "INDIAN CHANNEL",
        "channel_name": "Max cro",
        "srt_file": "805K IN 3WEEK.srt",
        "video_id": "LppHy0O25m4"
    },
    {
        "channel_group": "INDIAN CHANNEL",
        "channel_name": "Mind Gems",
        "srt_file": "1.3M VIEWS IN 1MONTH.srt",
        "video_id": "L9sJa-J5wI0"
    },
    {
        "channel_group": "INDIAN CHANNEL",
        "channel_name": "Old Tale",
        "srt_file": "281K IN 2WEEKS.srt",
        "video_id": "eSakZq7Kr1U"
    },
    {
        "channel_group": "",
        "channel_name": "Ink Explainer",
        "srt_file": "17M VIEWS IN 2MONTH.srt",
        "video_id": "49_Ph2q6uIM"
    },
    {
        "channel_group": "",
        "channel_name": "Ink Explainer",
        "srt_file": "416K VIEWS IN 2MONTH.srt",
        "video_id": "xmQk_oLVau0"
    },
    {
        "channel_group": "",
        "channel_name": "Joe Explain Everything",
        "srt_file": "1.1M IN 3MONTH.srt",
        "video_id": "os0KUojqFXo"
    },
    {
        "channel_group": "",
        "channel_name": "Joe Explain Everything",
        "srt_file": "27K IN 3MONTH.srt",
        "video_id": "kFA9A0iOlK4"
    },
    {
        "channel_group": "",
        "channel_name": "Lore Explained",
        "srt_file": "5.2M VIEWS IN 2WEEKS.srt",
        "video_id": "oGQRvdyFjM4"
    },
    {
        "channel_group": "",
        "channel_name": "Zenn",
        "srt_file": "8.1M IN 6MONTH.srt",
        "video_id": "st_Ah6Ykbh4"
    }
]

def sanitize_folder_name(name):
    # Remove characters not allowed in Windows folder names: \ / : * ? " < > |
    clean = re.sub(r'[\\/*?:"<>|]', '', name)
    clean = re.sub(r'\s+', ' ', clean).strip('. ')
    return clean[:100]

base_dir = r"d:\YOUTUBE VIDEOS STORAGE\The 10 videos"

results = []

for item in video_map:
    vid = item["video_id"]
    url = f"https://www.youtube.com/watch?v={vid}"
    print(f"Fetching metadata for {vid} ({item['channel_name']})...")
    p = subprocess.run(['yt-dlp', '-j', url], capture_output=True, text=True, errors='ignore')
    if p.returncode != 0 or not p.stdout.strip():
        print(f"Error fetching {vid}: {p.stderr}")
        continue
    
    meta = json.loads(p.stdout)
    title = meta.get("title", "")
    upload_date_raw = meta.get("upload_date", "")
    # Format YYYYMMDD into YYYY-MM-DD
    if len(upload_date_raw) == 8:
        upload_date = f"{upload_date_raw[:4]}-{upload_date_raw[4:6]}-{upload_date_raw[6:]}"
    else:
        upload_date = upload_date_raw
    views = meta.get("view_count", 0)
    duration_str = meta.get("duration_string", "")
    channel = meta.get("channel", item["channel_name"])

    # Determine channel folder
    if item["channel_group"]:
        channel_dir = os.path.join(base_dir, item["channel_group"], item["channel_name"])
    else:
        channel_dir = os.path.join(base_dir, item["channel_name"])

    src_srt_path = os.path.join(channel_dir, item["srt_file"])
    
    folder_name = sanitize_folder_name(title)
    video_dir = os.path.join(channel_dir, folder_name)
    os.makedirs(video_dir, exist_ok=True)

    # Copy srt into video_dir
    dest_srt_path = os.path.join(video_dir, f"{folder_name}.srt")
    if os.path.exists(src_srt_path):
        shutil.copy2(src_srt_path, dest_srt_path)
    
    # Read transcript content
    with open(src_srt_path, 'r', encoding='utf-8', errors='ignore') as f:
        transcript_content = f.read()

    # Create video_info.txt inside the video folder
    info_path = os.path.join(video_dir, "video_info.txt")
    info_content = f"""YouTube Video URL: {url}
Exact Video Title: {title}
Upload Date: {upload_date}
Current Views: {views:,}
Video Duration: {duration_str}
Channel: {channel}

============================================================
COMPLETE TRANSCRIPT (WITH TIMESTAMPS)
============================================================

{transcript_content}
"""
    with open(info_path, 'w', encoding='utf-8') as f:
        f.write(info_content)

    results.append({
        "channel": item["channel_name"],
        "group": item["channel_group"],
        "original_file": item["srt_file"],
        "folder_path": video_dir,
        "url": url,
        "title": title,
        "upload_date": upload_date,
        "views": views,
        "duration": duration_str,
        "first_lines": '\n'.join([line for line in transcript_content.splitlines() if line.strip() and not line.strip().isdigit() and '-->' not in line][:5])
    })

print("\n--- COMPLETED PROCESSING ALL VIDEOS ---")
summary_file = os.path.join(base_dir, "all_videos_summary.json")
with open(summary_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"Summary written to {summary_file}")
