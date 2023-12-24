import os
from pathlib import Path
import json
from urllib.parse import parse_qs, urlparse

def output_json_with_only_overlays(input):
    # Set paths
    memories = input / 'memories'
    memories_json = input / 'memories_history.json'

    # Read through files
    files = os.listdir(memories)

    # Set empty lists
    overlay_names = []
    new_json = []

    # Open memories_history.json
    with open(memories_json) as raw_json:
        meta_dict = json.load(raw_json)['Saved Media']

    # Loop through memories and see which ones have an overlay/caption
    for file in files:
        if 'overlay' in file:
            overlay_names.append(file.replace('-overlay', ''))

    # Go through the memories_history.json file and find the items which correspond to the names of files with overlay/captions
    for item in meta_dict:
        link = item['Download Link']
        mid = parse_qs(urlparse(link).query)["mid"][0]
        for name in overlay_names:
            if name.replace('.png', '') in mid or name.replace('mp4', '') in mid:
                new_json.append(item)

    # Create a dictionary in the same format as the initial memories_history.json file 
    new_json = {'Saved Media' : new_json}

    # Output the dictionary to a new json file
    with open(input / 'memories_history_new.json', 'w') as fp:
        json.dump(new_json, fp)


        
