import json
import urllib.request
import gzip
import xml.etree.ElementTree as ET
import os

def fetch_xml(url):
    print(f"Fetching: {url}")
    response = urllib.request.urlopen(url)
    content = response.read()
    if url.endswith('.gz'):
        return gzip.decompress(content)
    return content

def main():
    with open('config.json', 'r') as f:
        config = json.load(f)

    new_root = ET.Element("tv")
    new_root.set("generator-info-name", "MyCustomEPG-Mapper")

    for source in config['sources']:
        try:
            xml_data = fetch_xml(source['url'])
            tree = ET.fromstring(xml_data)
            # rename_map is like {"old_id": "new_id"}
            rename_map = source.get('rename_channels', {})
            target_ids = list(rename_map.keys())

            # 1. Process Channels
            for channel in tree.findall('channel'):
                old_id = channel.get('id')
                if old_id in target_ids:
                    new_id = rename_map[old_id]
                    channel.set('id', new_id) # Rename it!
                    new_root.append(channel)

            # 2. Process Programs
            for prog in tree.findall('programme'):
                old_channel_id = prog.get('channel')
                if old_channel_id in target_ids:
                    new_id = rename_map[old_channel_id]
                    prog.set('channel', new_id) # Rename it here too!
                    new_root.append(prog)
                    
        except Exception as e:
            print(f"Error processing {source['url']}: {e}")

    # Save as Gzip
    xml_str = ET.tostring(new_root, encoding='utf-8', xml_declaration=True)
    with gzip.open("custom_guide.xml.gz", "wb") as f:
        f.write(xml_str)
    
    with open("custom_guide.xml", "wb") as f:
        f.write(xml_str)
        
    print("Done! Mapped EPG created.")

if __name__ == "__main__":
    main()
