import json
import urllib.request
import gzip
import xml.etree.ElementTree as ET
import os
from datetime import datetime, timedelta, timezone # <--- Added timezone/timedelta

def fetch_xml(url):
    print(f"Fetching: {url}")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        content = response.read()
        if url.endswith('.gz') or content[:2] == b'\x1f\x8b':
            return gzip.decompress(content)
        return content
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None

def main():
    if not os.path.exists('config.json'):
        print("Error: config.json not found!")
        return

    with open('config.json', 'r') as f:
        config = json.load(f)

    # --- NEW: Set Singapore Time (UTC+8) ---
    sgt = timezone(timedelta(hours=8))
    now = datetime.now(sgt).strftime("%A, %d %b %Y - %I:%M %p SGT")
    
    new_root = ET.Element("tv")
    # This text will appear in TiviMate Source Info
    new_root.set("generator-info-name", f"MyCloudEPG ({now})")

    channels_added = 0
    programs_added = 0

    for source in config.get('sources', []):
        url = source.get('url')
        rename_map = source.get('rename_channels', {})
        
        if not url or not rename_map:
            continue

        xml_data = fetch_xml(url)
        if not xml_data:
            continue

        try:
            tree = ET.fromstring(xml_data)
            target_ids = list(rename_map.keys())

            for channel in tree.findall('channel'):
                old_id = channel.get('id')
                if old_id in target_ids:
                    new_id = rename_map[old_id]
                    channel.set('id', new_id)
                    new_root.append(channel)
                    channels_added += 1

            for prog in tree.findall('programme'):
                old_channel_id = prog.get('channel')
                if old_channel_id in target_ids:
                    new_id = rename_map[old_channel_id]
                    prog.set('channel', new_id)
                    new_root.append(prog)
                    programs_added += 1
                    
        except Exception as e:
            print(f"Error parsing XML from {url}: {e}")

    xml_str = ET.tostring(new_root, encoding='utf-8', xml_declaration=True)

    with open("custom_guide.xml", "wb") as f:
        f.write(xml_str)
    
    with gzip.open("custom_guide.xml.gz", "wb") as f:
        f.write(xml_str)

    print(f"Success! Added {channels_added} channels and {programs_added} programs.")
    print(f"SGT Timestamp: {now}")

if __name__ == "__main__":
    main()
    
