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
    # 1. Load your config
    with open('config.json', 'r') as f:
        config = json.load(f)

    # 2. Create the root of our new XML file
    new_root = ET.Element("tv")
    new_root.set("generator-info-name", "MyCustomEPG")

    # To store programs after we collect all channels
    all_programs = []
    included_ids = set()

    # 3. Process each source
    for source in config['sources']:
        try:
            xml_data = fetch_xml(source['url'])
            tree = ET.fromstring(xml_data)
            target_ids = source['include_channels']
            included_ids.update(target_ids)

            # Find and add <channel> nodes
            for channel in tree.findall('channel'):
                if channel.get('id') in target_ids:
                    new_root.append(channel)

            # Find and add <programme> nodes
            for prog in tree.findall('programme'):
                if prog.get('channel') in target_ids:
                    all_programs.append(prog)
        except Exception as e:
            print(f"Error processing {source['url']}: {e}")

    # 4. Append programs at the end (Standard XMLTV format)
    for prog in all_programs:
        new_root.append(prog)

    # 5. Save the file
    new_tree = ET.ElementTree(new_root)
    ET.indent(new_tree, space="  ", level=0) # Make it readable
    new_tree.write("custom_guide.xml", encoding="utf-8", xml_declaration=True)
    print("Done! custom_guide.xml created.")

if __name__ == "__main__":
    main()
