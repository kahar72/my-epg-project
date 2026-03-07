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
    new_root.set("generator-info-name", "MyCustomEPG")

    all_programs = []
    included_ids = set()

    for source in config['sources']:
        try:
            xml_data = fetch_xml(source['url'])
            tree = ET.fromstring(xml_data)
            target_ids = source['include_channels']
            included_ids.update(target_ids)

            for channel in tree.findall('channel'):
                if channel.get('id') in target_ids:
                    new_root.append(channel)

            for prog in tree.findall('programme'):
                if prog.get('channel') in target_ids:
                    all_programs.append(prog)
        except Exception as e:
            print(f"Error processing {source['url']}: {e}")

    for prog in all_programs:
        new_root.append(prog)

    new_tree = ET.ElementTree(new_root)
    ET.indent(new_tree, space="  ", level=0)
    
    # --- NEW: SAVE AS GZIP ---
    xml_str = ET.tostring(new_root, encoding='utf-8', xml_declaration=True)
    with gzip.open("custom_guide.xml.gz", "wb") as f:
        f.write(xml_str)
    
    # Also keep the regular version if you want for testing
    with open("custom_guide.xml", "wb") as f:
        f.write(xml_str)
        
    print("Done! Compressed custom_guide.xml.gz created.")

if __name__ == "__main__":
    main()
